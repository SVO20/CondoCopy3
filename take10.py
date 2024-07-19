"""
SD-cards insertion monitoring and identification using async console (curses).

To use curses on Windows:
1. Install windows-curses:
pip install windows-curses

2. Refer to:
https://stackoverflow.com/questions/16740385/python-curses-redirection-is-not-supported
https://i.sstatic.net/hQ814.png
in PyCharm IDE
if
initscr(): LINES=1 COLS=80: too small.   exception occured
use    os.system("mode con cols=80 lines=60")
in     main()
"""

import asyncio
from collections import deque
from datetime import datetime
import os
import ctypes
import zlib
from typing import Tuple

import curses
import psutil


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


async def get_removable_drives():
    partitions = psutil.disk_partitions()
    removable_drives = [p.device for p in partitions if 'removable' in p.opts]
    return removable_drives


async def update_drives(deque_removables: deque):
    set_current_removables = set(await get_removable_drives())
    set_deque_removables = {drive['device'] for drive in deque_removables}
    updated = False

    # Add new drives
    for drive in set_current_removables - set_deque_removables:
        drive_id = generate_id(drive)

        # deque_removables format --v
        # deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
        deque_removables.append({'device': drive, 'id': drive_id})
        updated = True

    # Remove disconnected drives
    for drive in list(deque_removables):
        if drive['device'] not in set_current_removables:
            deque_removables.remove(drive)
            updated = True

    return updated


async def refresh_display(stdscr, deque_removables):
    stdscr.clear()
    for line, drive in enumerate(deque_removables):
        # Place string in position  (line, col,...  of the terminal
        stdscr.addstr(line, 0, f"{drive['device']} (Removable) ID: {drive['id']}")
    stdscr.refresh()


async def main(stdscr):
    # deque_removables format --v
    # deque([{'device': str(drive), 'id': str(drive_id)}, ... ])
    deque_removables = deque()
    while True:
        updated = await update_drives(deque_removables)
        if updated:
            await refresh_display(stdscr, deque_removables)
        await asyncio.sleep(1)


def curses_main(stdscr):
    asyncio.run(main(stdscr))


if __name__ == "__main__":
    os.system("mode con cols=80 lines=12")  # for right PyCharm terminal emulation

    curses.wrapper(curses_main)



