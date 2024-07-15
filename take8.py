import os
import shutil
import asyncio
import aiofiles
import win32file
import win32con


def choose_buffer_size(file_size):
    if file_size < 1 * 1024 * 1024:  # less than 1 MB, then
        return 64 * 1024                                    # 64 KB
    elif file_size < 100 * 1024 * 1024:  # less than 100 MB, then
        return 1 * 1024 * 1024                                      # 1 MB
    else:                                   # greater than 100 MB, then
        return 16 * 1024 * 1024                                         # 16 MB


async def copy_file(src, dst):
    file_size = os.path.getsize(src)
    buffer_size = choose_buffer_size(file_size)

    async with aiofiles.open(src, 'rb') as fsrc:
        async with aiofiles.open(dst, 'wb') as fdst:
            while True:
                data = await fsrc.read(buffer_size)
                if not data:
                    break
                await fdst.write(data)

    shutil.copystat(src, dst)

    st = os.stat(src)
    os.utime(dst, (st.st_atime, st.st_mtime))

    creation_time = win32file.GetFileTime(
        win32file.CreateFile(src, win32con.GENERIC_READ, 0, None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None))[0]
    win_file = win32file.CreateFile(
        dst, win32con.GENERIC_WRITE, 0, None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None)
    win32file.SetFileTime(win_file, creation_time, None, None)
    win_file.close()


async def copy_files(file_list, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    tasks = []
    for file_path in file_list:
        if os.path.exists(file_path):
            dst_path = os.path.join(dst_dir, os.path.basename(file_path))
            tasks.append(copy_file(file_path, dst_path))

    await asyncio.gather(*tasks)


def read_file_list(filelist_path):
    with open(filelist_path, 'r') as f:
        lines = f.readlines()
    files_to_delete = lines[:-1]
    disk2 = lines[-1].strip()
    return files_to_delete, disk2


# usage
# todo debug copy module
file_list = read_file_list('filelist.txt')
dst_dir = 'c:\\'
asyncio.run(copy_files(file_list, dst_dir))
