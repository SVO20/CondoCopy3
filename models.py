import asyncio
from collections import deque, Counter
from datetime import datetime
from typing import Optional, Tuple
import os
import ctypes
import zlib
import numpy as np
import psutil
from PyQt5.QtCore import pyqtSignal, QObject
from logger import success, trace


class RemovableDevicesPoolModel(QObject):
    devices_changed = pyqtSignal(list)  # Signal for device changes

    def __init__(self, cameras):
        super().__init__()
        self.devices = deque()
        self.cameras = cameras

    async def monitor_removables(self):
        # Continuously monitor removable devices
        while True:
            set_current_removables = set(await get_removable_drives())
            set_last_removables = {drive['device'] for drive in self.devices}
            is_updated = False

            # Check for new connected removables
            for drive in set_current_removables - set_last_removables:
                drive_id = generate_id(drive)
                camera_model = match_camera_model(drive, self.cameras)
                self.devices.append({'device': drive, 'id': drive_id, 'model': camera_model})
                success(f"The removable is matched with: {camera_model}")
                is_updated = True

            # Check for disconnected drives
            for drive in list(self.devices):
                if drive['device'] not in set_current_removables:
                    self.devices.remove(drive)
                    success(f"The removable [{drive['id']}] was disconnected")
                    is_updated = True

            trace(f"{self.devices = }")
            if is_updated:
                self.devices_changed.emit(self.get_devices())  # Signal about device changes

            await asyncio.sleep(1)

    def get_devices(self):
        return list(self.devices)


async def get_removable_drives() -> list:
    # Get the list of currently connected removable drives
    partitions = psutil.disk_partitions()
    removable_drives = [p.device for p in partitions if 'removable' in p.opts]
    return removable_drives


def get_directories(start_path) -> list:
    """Get a list of related directories for the given path"""
    apath = os.path.abspath(start_path)
    rel_directories = []
    for root, dirs, files in os.walk(apath):
        for dir_name in dirs:
            # Append relative path from abs path "root + dir_name" that started from  apath
            rel_directories.append(os.path.relpath(os.path.join(root, dir_name), apath))
    return rel_directories


def calculate_weights(cameras_data) -> dict:
    """Calculate token weights based on their frequency in cameras_data"""
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

    # Sorting models by specificity/complexity (token weights)
    sorted_models = sorted(relevant_models.items(),
                           key=lambda item: np.sum(model_vectors[item[0]]), reverse=True)

    # Return the first camera model (with the highest complexity)
    return sorted_models[0][0] if sorted_models else None


def get_volume_info_kernel32(drive_letter: str) -> Tuple[str, str, int]:
    """Retrieves the volume label, volume serial number, and total size of the drive specified by the given drive letter."""
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
        return datetime.fromtimestamp(stat.st_ctime).strftime('%Y%m%d_%H%M%S')
    except (FileNotFoundError, OSError):
        return ""


def generate_id(drive):
    """Generates a unique ID for a drive based on its volume information and creation dates of specific folders."""
    distinst_folders = ("DCIM", "MISC", "Android")

    volume_label, volume_serial, total_size = get_volume_info_kernel32(drive)
    str_creation_dates = "".join([get_folder_creation_date(os.path.join(drive, folder))
                                  for folder in distinst_folders])

    combined_str = f"{volume_label}{volume_serial}{total_size}{str_creation_dates}"
    crc32_hash = zlib.crc32(combined_str.encode())
    hash_suffix = f"{crc32_hash:08x}"[:6].upper()

    return f"{volume_label}_{hash_suffix}"
