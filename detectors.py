"""
Module provides functionality to detect removables and match theis dir structures with camera model

"""

import ctypes
import os
import zlib
from collections import Counter
from datetime import datetime
from typing import Optional, Tuple

import numpy as np
import toml





def get_directories(start_path) -> list:
    """Get a list of related directories for the given path"""
    apath = os.path.abspath(start_path)
    rel_directories = []
    for root, dirs, files in os.walk(apath):
        for dir_name in dirs:
            # append relative path from abs path "root + dir_name" that started from  apath
            rel_directories.append(os.path.relpath(os.path.join(root, dir_name), apath))
    return rel_directories


def calculate_weights(cameras_data) -> dict[str, float]:
    """Calculate token weights based on their frequency in  cameras_data  """
    all_tokens = [token
                  for item in cameras_data.values()
                  for token in item['structure']]
    token_counts = Counter(all_tokens)
    token_weights = {token: 1 / count for token, count in token_counts.items()}
    return token_weights


def match_camera_model(sd_path, cameras: dict) -> Optional[str]:
    """Matches the SD card structure to a camera model"""
    s_sd_directories = set(get_directories(sd_path))

    # Filtering camera models that have all directories present on the given SD card
    relevant_models = {}
    for model, data in cameras.items():
        if set(data['structure']).issubset(s_sd_directories):
            relevant_models[model] = data

    print(relevant_models)
    if not relevant_models:
        return None

    # Tokenization and calculation of base and additional weights
    base_weights = calculate_weights(cameras)
    additional_weights = calculate_weights(relevant_models)

    # Calculate resulting weights as the sum of base and additional weights
    resulting_weights = {token: base_weights.get(token, 0) + additional_weights.get(token, 0)
                         for token in additional_weights}

    # Vectorization of camera models using resulting weights
    model_vectors = {}
    for model, data in relevant_models.items():
        vector = np.array([resulting_weights[dir] for dir in data['structure']])
        model_vectors[model] = vector

    # Sorting models by specifity/complexity (token weights)
    sorted_models = sorted(relevant_models.items(),
                           key=lambda item: np.sum(model_vectors[item[0]]), reverse=True)

    # Return the first camera model (with the highest complexity)
    return sorted_models[0][0] if sorted_models else None


def get_volume_info_kernel32(drive_letter: str) -> Tuple[str, str, int]:
    """/GPT-assisted/
    Retrieves the volume label, volume serial number, and total size of the drive
    specified by the given drive letter.

    Args:
        drive_letter (str): The letter of the drive, which can be provided as a single letter,
        with or without a colon, or with a backslash (e.g. 'C', 'C:', or 'C:\\').

    Returns:
        Tuple[str, str, int]:
        A tuple containing the volume label (str), volume serial number (str),
        and the total size of the drive in bytes (int). If the volume label cannot be retrieved,
        'NO_LABEL' is returned, and if the size cannot be determined, 0 is returned.
    """
    if 4 >= len(drive_letter) > 1:
        drive_letter = drive_letter[0].upper()
    if not (len(drive_letter) == 1 and drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        raise ValueError("Invalid drive letter format. Expected format is 'X:' or a single letter")
    drive_letter += ":\\"

    kernel32 = ctypes.windll.kernel32
    volume_name_buffer = ctypes.create_unicode_buffer(1024)
    file_system_name_buffer = ctypes.create_unicode_buffer(1024)
    serial_number = ctypes.c_uint(0)
    max_component_length = ctypes.c_uint(0)
    file_system_flags = ctypes.c_uint(0)

    free_bytes_available = ctypes.c_ulonglong(0)
    total_number_of_bytes = ctypes.c_ulonglong(0)
    total_number_of_free_bytes = ctypes.c_ulonglong(0)

    if kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive_letter),
        volume_name_buffer,
        ctypes.sizeof(volume_name_buffer),
        ctypes.byref(serial_number),
        ctypes.byref(max_component_length),
        ctypes.byref(file_system_flags),
        file_system_name_buffer,
        ctypes.sizeof(file_system_name_buffer)
    ):
        volume_label = volume_name_buffer.value or "NO_LABEL"
        volume_serial = f"{serial_number.value:08X}"
    else:
        volume_label = "NO_LABEL"
        volume_serial = ""

    if kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(drive_letter),
        ctypes.byref(free_bytes_available),
        ctypes.byref(total_number_of_bytes),
        ctypes.byref(total_number_of_free_bytes)
    ):
        total_size = total_number_of_bytes.value
    else:
        total_size = 0

    return volume_label, volume_serial, total_size


def get_folder_creation_date(path):
    try:
        stat = os.stat(path)
        # YYYYMMDD_HHMMSS format --v
        return datetime.fromtimestamp(stat.st_ctime).strftime('%Y%m%d_%H%M%S')
    except (FileNotFoundError, OSError):
        # Handling 'no such folder' exception (pass)
        # Handling OS reading errors, also in case of encrypted disks (pass)
        return ""


def generate_id(drive):
    """Generates a unique ID for a drive based on its volume information and
     creation dates of specific folders (if presented on drive and available to retrieve).

    The ID is constructed using the following steps:
    1. Get volume label, volume serial number, and total size of the drive
    2. Get the distinst folders creation dates ("" if there is no folder on the drive) and
        concat into a single string
    3. Concat the volume label, volume serial number, total size, and folder creation dates
        into a single string
    4. Calculate the CRC32 checksum of the combined string
    5. Use the first six characters of the CRC32 checksum (in uppercase) as a suffix for the ID
    6. Compose the final ID in the format "VOLUME_LABEL_HASH_SUFFIX".
    """

    # Folders which creation dates to be used as unique marks  (if exists and available)
    distinst_folders = ("DCIM", "MISC", "Android")

    volume_label, volume_serial, total_size = get_volume_info_kernel32(drive)
    str_creation_dates = "".join([get_folder_creation_date(os.path.join(drive, folder))
                                  for folder in distinst_folders])

    # Create the string to be hashed and calculate its CRC32 checksum
    combined_str = f"{volume_label}{volume_serial}{total_size}{str_creation_dates}"
    crc32_hash = zlib.crc32(combined_str.encode())
    # use six first chars
    hash_suffix = f"{crc32_hash:08x}"[:6].upper()

    # compose and return ID
    return f"{volume_label}_{hash_suffix}"
