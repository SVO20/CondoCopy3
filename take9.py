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


def Win32_API_copy_file_times(src, dst):
    HANDLE_src_file = win32file.CreateFile(src, win32con.GENERIC_READ, 0, None,
                                           win32con.OPEN_EXISTING,
                                           win32con.FILE_ATTRIBUTE_NORMAL, None)
    try:
        creation_time, access_time, write_time = win32file.GetFileTime(HANDLE_src_file)
    except Exception as e:
        print(f"Failed to get file times from source file by Win32_API: {e}")
        creation_time = access_time = write_time = None
    finally:
        HANDLE_src_file.close()

    HANDLE_dst_file = win32file.CreateFile(dst, win32con.GENERIC_WRITE, 0, None,
                                           win32con.OPEN_EXISTING,
                                           win32con.FILE_ATTRIBUTE_NORMAL, None)
    try:
        if creation_time:
            win32file.SetFileTime(HANDLE_dst_file, creation_time, access_time, write_time)
        else:
            win32file.SetFileTime(HANDLE_dst_file, None, access_time, write_time)
    except Exception as e:
        print(f"Failed to set file times on destination file by Win32_API: {e}")
    finally:
        HANDLE_dst_file.close()


async def copy_file(src, dst) -> None:
    file_size = os.path.getsize(src)
    buffer_size = choose_buffer_size(file_size)

    async with aiofiles.open(src, 'rb') as fsrc:
        # REWRITE EXISTING mode
        async with aiofiles.open(dst, 'wb') as fdst:
            while True:
                data = await fsrc.read(buffer_size)
                if not data:
                    break
                await fdst.write(data)

    # Copy all possible file stats (including a_time and m_time)
    shutil.copystat(src, dst)

    # Explicit copy file times (c_time, a_time and m_time) by Win32_API
    # this enshuring to be disabled further
    Win32_API_copy_file_times(src, dst)


def is_identical_file(src, dst):
    """Compare src and dst file by plenty of characteristics"""

    if not (os.path.exists(src) and os.path.exists(dst)):
        return False
    if os.path.getsize(src) != os.path.getsize(dst):
        return False
    if os.path.basename(src) != os.path.basename(dst):
        return False

    # Check only times using os.stat
    src_stat = os.stat(src)
    dst_stat = os.stat(dst)
    if (src_stat.st_atime, src_stat.st_mtime, src_stat.st_ctime) != \
       (dst_stat.st_atime, dst_stat.st_mtime, dst_stat.st_ctime):
        return False

    # Compare the first and last  n_to_compare  bytes
    n_to_compare = 1024
    with open(src, 'rb') as fsrc, open(dst, 'rb') as fdst:
        # Directly compare first  n_to_compare  bytes
        src_start = fsrc.read(n_to_compare)
        fdst_start = fdst.read(n_to_compare)
        if src_start != fdst_start:
            return False

        # Directly compare last  n_to_compare  bytes (if size allows)
        if os.path.getsize(src) > n_to_compare:
            fsrc.seek(-n_to_compare, os.SEEK_END)
            fdst.seek(-n_to_compare, os.SEEK_END)

            src_end = fsrc.read(n_to_compare)
            fdst_end = fdst.read(n_to_compare)
            if src_end != fdst_end:
                return False

    return True


async def move_file(src, dst) -> None:
    await copy_file(src, dst)
    # v-- blocking --v
    if is_identical_file(src, dst):
        os.remove(src)
        print(f"Deleted source file via moving: {os.path.basename(src)}")
    else:
        raise IOError(f"Files {src} and {dst} are not identical! Halting!")


async def copy_files(file_list, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    tasks = []
    for file_path in file_list:
        if os.path.exists(file_path):
            dst_path = os.path.join(dst_dir, os.path.basename(file_path))
            tasks.append(copy_file(file_path, dst_path))

    await asyncio.gather(*tasks)


async def move_files(file_list, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    tasks = []
    for file_path in file_list:
        if os.path.exists(file_path):
            dst_path = os.path.join(dst_dir, os.path.basename(file_path))
            tasks.append(move_file(file_path, dst_path))

    await asyncio.gather(*tasks)

# usage
file_list, dst_dir = read_file_list('filelist.txt')
#asyncio.run(copy_files(file_list, dst_dir))

asyncio.run(move_files(file_list, dst_dir))