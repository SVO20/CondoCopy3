"""
Other approach to SD-cards insertion monitoring.

using async console (curses) and identification via Windows vol SERIAL_NUMBER

curses on windows:
                    pip install windows-curses
AND
https://stackoverflow.com/questions/16740385/python-curses-redirection-is-not-supported
https://i.sstatic.net/hQ814.png
in PyCharm IDE
if
initscr(): LINES=1 COLS=80: too small.   exception occured
use    os.system("mode con cols=80 lines=60")
in     main()
"""

import asyncio
import os

import psutil
import subprocess
import curses
from collections import deque


async def get_removable_drives():
    partitions = psutil.disk_partitions()
    removable_drives = [p.device for p in partitions if 'removable' in p.opts]
    return removable_drives


async def get_serial_number(drive_letter):
    try:
        # call system util  vol  and parse its stdout
        command = f"vol {drive_letter}:"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            if s_n := result.stdout.split(':')[-1].strip():
                return s_n
            else:
                raise Exception(f"Curious 'vol' command output!")
        return None
    except Exception as e:
        return None


async def update_drives(deque_removables: deque):
    set_current_removables = set(await get_removable_drives())
    set_deque_removables = {drive['device'] for drive in deque_removables}
    updated = False

    # Add new drives
    for drive in set_current_removables - set_deque_removables:
        ch_drive_letter = drive.split(':')[0]
        str_serial_number = str(await get_serial_number(ch_drive_letter))

        # deque_removables format --v
        # deque([{'device': str(drive), 'serial_number': str(serial_number)}, ... ])
        deque_removables.append({'device': drive, 'serial_number': str_serial_number})
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
        stdscr.addstr(line, 0, f"{drive['device']} (Removable) S/N: {drive['serial_number']}")
    stdscr.refresh()


async def main(stdscr):
    # deque_removables format --v
    # deque([{'device': str(drive), 'serial_number': str(serial_number)}, ... ])
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

    """
    As result: Volume SERIAL_NUMBER often 00000-00000
    
    :(
    """


