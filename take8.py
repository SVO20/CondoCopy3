"""
This module provides asynchronous file copy functionality using  aiofiles.

includes the functions to read a file list, determine buffer sizes, copy files with file stats,
and manage file copy tasks.
"""

import os
import shutil
import asyncio
import aiofiles
import win32file
import win32con


def read_file_list(filelist_path):
    with open(filelist_path, 'r') as f:
        lines = f.readlines()
    l_files_to_delete = [os.path.abspath(s.strip()) for s in lines[:-1]]
    disk2 = lines[-1].strip()
    return l_files_to_delete, disk2


def choose_buffer_size(file_size):
    if file_size < 1 * 1024 * 1024:  # less than 1 MB, then
        return 64 * 1024                                    # 64 KB
    elif file_size < 100 * 1024 * 1024:  # less than 100 MB, then
        return 1 * 1024 * 1024                                      # 1 MB
    else:                                   # greater than 100 MB, then
        return 16 * 1024 * 1024                                         # 16 MB


async def copy_file(src, dst) -> None:
    file_size = os.path.getsize(src)
    buffer_size = choose_buffer_size(file_size)

    async with aiofiles.open(src, 'rb') as fsrc:
        async with aiofiles.open(dst, 'wb') as fdst:
            while True:
                data = await fsrc.read(buffer_size)
                if not data:
                    break
                await fdst.write(data)

    # Copy file stats including a_time and m_time
    shutil.copystat(src, dst)

    # # Explicit copy file stats including a_time and m_time using
    # st = os.stat(src)
    # os.utime(dst, (st.st_atime, st.st_mtime))

    # Copy CreationTime by Win32_API routine
    HANDLE_src_file = win32file.CreateFile(src, win32con.GENERIC_READ, 0, None,
                                           win32con.OPEN_EXISTING,
                                           win32con.FILE_ATTRIBUTE_NORMAL, None)
    creation_time = win32file.GetFileTime(HANDLE_src_file)[0]
    HANDLE_src_file.close()

    HANDLE_dst_file = win32file.CreateFile(dst, win32con.GENERIC_WRITE, 0, None,
                                           win32con.OPEN_EXISTING,
                                           win32con.FILE_ATTRIBUTE_NORMAL, None)
    win32file.SetFileTime(HANDLE_dst_file, creation_time, None, None)
    HANDLE_dst_file.close()


async def copy_files(file_list, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    tasks = []
    for file_path in file_list:
        if os.path.exists(file_path):
            dst_path = os.path.join(dst_dir, os.path.basename(file_path))
            tasks.append(copy_file(file_path, dst_path))

    await asyncio.gather(*tasks)


# usage
file_list, dst_dir = read_file_list('filelist.txt')
asyncio.run(copy_files(file_list, dst_dir))
