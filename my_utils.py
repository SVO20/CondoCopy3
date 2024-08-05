import base64
import os
import zlib
from datetime import datetime, timedelta
from typing import Optional
import ctypes
import os
import zlib
from collections import Counter
from datetime import datetime
from typing import Optional, Tuple

import numpy as np
import psutil
import toml


def expand_compressed(bytes) -> str:
    # Decompresses and decodes bytes that were compressed and encoded
    return zlib.decompress(base64.b64decode(bytes)).decode('utf-8')


def dtstring_to_compactformat(datestring, utc: int = 3) -> Optional[str]:
    """/GPT-assisted/
    Convert various date-time string formats to compact standard YYYYMMDD_HHMMSS format.

    :param datestring: The date-time string to be converted.
    :param utc: Time shift (poisitive or negative)
                Default is UTC+3 time zone, Standard Time (Moscow/Ankara), non-Daylight Saving
    :return: The date-time string in YYYYMMDD_HHMMSS format or None if conversion is not possible.
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",       # Example: 2023-07-18 14:30:45 (ISO 8601)
        "%Y-%m-%d %H:%M",          # Example: 2023-07-18 14:30 (ISO 8601 without seconds)
        "%Y/%m/%d %H:%M:%S",       # Example: 2023/07/18 14:30:45
        "%Y/%m/%d %H:%M",          # Example: 2023/07/18 14:30
        "%d-%m-%Y %H:%M:%S",       # Example: 18-07-2023 14:30:45 (European format)
        "%d-%m-%Y %H:%M",          # Example: 18-07-2023 14:30 (European format without seconds)
        "%d/%m/%Y %H:%M:%S",       # Example: 18/07/2023 14:30:45 (European format)
        "%d/%m/%Y %H:%M",          # Example: 18/07/2023 14:30 (European format without seconds)
        "%m/%d/%Y %H:%M:%S",       # Example: 07/18/2023 14:30:45 (US format)
        "%m/%d/%Y %H:%M",          # Example: 07/18/2023 14:30 (US format without seconds)
        "%Y%m%d_%H%M%S",           # Example: 20230718_143045 (Compact format with separator)
        "%Y%m%d%H%M%S",            # Example: 20230718143045 (Compact format without separator)
        "%Y%m%d %H%M%S",           # Example: 20230718 143045 (Compact format with space separator)
        "%Y%m%d-%H%M%S",           # Example: 20230718-143045 (Compact format with dash separator)
        "%Y%m%d.%H%M%S",           # Example: 20230718.143045 (Compact format with dot separator)
        "%Y:%m:%d %H:%M:%S",       # Example: 2023:07:18 14:30:45 (Exif format)
        "%Y:%m:%d %H:%M",          # Example: 2023:07:18 14:30 (Exif format without seconds)
        "%d %b %Y %H:%M:%S",       # Example: 18 Jul 2023 14:30:45 (Verbose date format)
        "%d %b %Y %H:%M",          # Example: 18 Jul 2023 14:30 (Verbose date format without seconds)
        "%b %d, %Y %H:%M:%S",      # Example: Jul 18, 2023 14:30:45 (Verbose date format)
        "%b %d, %Y %H:%M",         # Example: Jul 18, 2023 14:30 (Verbose date format without seconds)
        "%Y.%m.%d %H:%M:%S",       # Example: 2023.07.18 14:30:45 (Dot-separated format)
        "%Y.%m.%d %H:%M",          # Example: 2023.07.18 14:30 (Dot-separated format without seconds)
        "%d.%m.%Y %H:%M:%S",       # Example: 18.07.2023 14:30:45 (Dot-separated European format)
        "%d.%m.%Y %H:%M",          # Example: 18.07.2023 14:30 (Dot-separated European format without seconds)
        "%Y%m%d %H%M",             # Example: 20230718 1430 (Compact format with space separator without seconds)
        "%Y%m%d_%H%M",             # Example: 20230718_1430 (Compact format with separator without seconds)
        "%Y%m%d-%H%M",             # Example: 20230718-1430 (Compact format with dash separator without seconds)
        "%Y%m%d.%H%M",             # Example: 20230718.1430 (Compact format with dot separator without seconds)
        "%Y-%m-%dT%H:%M:%S.%fZ",   # Example: 2023-07-18T14:30:45.123Z (ISO 8601 with milliseconds and Zulu time)
        "%Y-%m-%dT%H:%M:%S.%f%z",  # Example: 2023-07-18T14:30:45.123+0200 (ISO 8601 with milliseconds and UTC offset)
        "%Y-%m-%dT%H:%M:%S%z",     # Example: 2023-07-18T14:30:45+0200 (ISO 8601 with UTC offset)
        "%Y-%m-%dT%H:%M.%fZ",      # Example: 2023-07-18T14:30.123Z (ISO 8601 with milliseconds without seconds and Zulu time)
        "%Y-%m-%dT%H:%M.%f%z",     # Example: 2023-07-18T14:30.123+0200 (ISO 8601 with milliseconds without seconds and UTC offset)
        "%Y-%m-%dT%H:%M%z",        # Example: 2023-07-18T14:30+0200 (ISO 8601 without seconds and UTC offset)
        "%Y-%m-%d %H:%M:%S.%f",    # Example: 2023-07-18 14:30:45.123 (Date with milliseconds)
        "%Y-%m-%d %H:%M.%f",       # Example: 2023-07-18 14:30.123 (Date with milliseconds without seconds)
        "%Y%m%dT%H%M%SZ",          # Example: 20230718T143045Z (Compact ISO 8601 with Zulu time)
        "%Y%m%dT%H%M%S%z",         # Example: 20230718T143045+0200 (Compact ISO 8601 with UTC offset)
        "%Y%m%dT%H%MZ",            # Example: 20230718T1430Z (Compact ISO 8601 without seconds and Zulu time)
        "%Y%m%dT%H%M%z"            # Example: 20230718T1430+0200 (Compact ISO 8601 without seconds and UTC offset)
    ]
    # Check the date absense
    if not datestring:
        return None

    # Check if the date is a float, which might represent a UNIX timestamp
    if isinstance(datestring, float):
        try:
            # Convert UNIX timestamp to datetime
            dt = datetime.utcfromtimestamp(datestring)
            return dt.strftime("%Y%m%d_%H%M%S")
        except Exception as e:
            return None  # Return None if conversion fails

    datestring = str(datestring)

    # Check if the string with date contain  'UTC'  mark
    is_utc_time = datestring.find("UTC") != -1
    if is_utc_time:
        # Apply UTC time shift
        # !default! is  UTC+3  - Moscow/Ankara standart time
        delta = timedelta(hours=utc)
        # Clear 'UTC' mark
        datestring = datestring.replace('UTC', '').strip()
    else:
        delta = timedelta(hours=0)

    # Check if the datetime corresponds one of the formats (from more frequent used to less /GPT/)
    for fmt in formats:
        try:
            # Try to parse the date string with the current format
            dt = datetime.strptime(datestring, fmt)
            dt = dt + delta

            if '%S' in fmt:
                # normal
                return dt.strftime("%Y%m%d_%H%M%S")
            else:
                # If the format does not include seconds, add "00" for seconds
                return dt.strftime("%Y%m%d_%H%M00")

        except ValueError:
            # If parsing fails, continue to the next format
            continue

    return None  # Return None if no formats matched


def get_folder_creation_date(path):
    try:
        stat = os.stat(path)
        # YYYYMMDD_HHMMSS format --v
        return datetime.fromtimestamp(stat.st_ctime).strftime('%Y%m%d_%H%M%S')
    except (FileNotFoundError, OSError):
        # Handling 'no such folder' exception (pass)
        # Handling OS reading errors, also in case of encrypted disks (pass)
        return ""

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

async def get_removable_drives() -> list:
    partitions = psutil.disk_partitions()
    removable_drives = [p.device for p in partitions if 'removable' in p.opts]
    return removable_drives


def get_directories(start_path) -> list:
    """Get a list of related directories for the given path"""
    apath = os.path.abspath(start_path)
    rel_directories = []
    for root, dirs, files in os.walk(apath):
        for dir_name in dirs:
            # append relative path from abs path "root + dir_name" that started from  apath
            rel_directories.append(os.path.relpath(os.path.join(root, dir_name), apath))
    return rel_directories

