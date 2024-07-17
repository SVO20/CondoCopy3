import os
import shutil
import asyncio
import aiofiles
import win32file
import win32con
import psutil


def read_file_list(filelist_path):
    with open(filelist_path, 'r') as f:
        lines = f.readlines()
    l_files_to_delete = [os.path.abspath(s.strip()) for s in lines[:-1]]
    disk2 = lines[-1].strip()
    return l_files_to_delete, disk2


def choose_buffer_size(file_size):
    if file_size < 1 * 1024 * 1024:  # less than 1 MB
        return 64 * 1024  # 64 KB
    elif file_size < 100 * 1024 * 1024:  # less than 100 MB
        return 1 * 1024 * 1024  # 1 MB
    else:  # greater than 100 MB
        return 16 * 1024 * 1024  # 16 MB


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


async def copy_file(src, dst, semaphore) -> None:
    async with semaphore:  # Use semaphore to limit concurrency
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


async def move_file(src, dst, semaphore) -> None:
    await copy_file(src, dst, semaphore)
    # v-- blocking --v
    if is_identical_file(src, dst):
        os.remove(src)
        print(f"Deleted source file via moving: {os.path.basename(src)}")
    else:
        raise IOError(f"Files {src} and {dst} are not identical! Halting!")


def get_disk_type(path):
    # Simplified method to determine disk type
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if path.startswith(partition.mountpoint):
            return partition.opts
    return 'unknown'


def max_concurrent_copy_threads_algorithm(src_paths, dst_path):
    # Get the number of CPU cores
    cpu_count = psutil.cpu_count(logical=True)
    # Get the amount of available memory in GB
    available_memory_gb = psutil.virtual_memory().available / (1024 ** 3)
    # Get the type of source and destination disks
    src_disk_type = get_disk_type(src_paths[0])  # Get disk info of first file to copy
    dst_disk_type = get_disk_type(dst_path)
    # Get the current CPU load
    cpu_load = psutil.cpu_percent(interval=1)

    # Base number of concurrent copies
    base_count = 2

    # Increase base count depending on the number of cores
    if cpu_count > 4:
        base_count += 2
    elif cpu_count > 2:
        base_count += 1

    # Increase base count depending on the amount of available memory
    if available_memory_gb > 8:
        base_count += 2
    elif available_memory_gb > 4:
        base_count += 1

    # Increase base count depending on the type of disks
    if 'SSD' in src_disk_type:
        base_count += 1
    if 'SSD' in dst_disk_type:
        base_count += 1

    # Decrease count if CPU load is high
    if cpu_load > 70:
        base_count -= 1

    # Limit minimum and maximum count
    base_count = max(1, min(base_count, 8))

    print(f"Proceeding with the {base_count} concurrent IO operations...")
    return base_count


async def copy_files(file_list, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    max_concurrent_copies = max_concurrent_copy_threads_algorithm(file_list, dst_dir)
    semaphore = asyncio.Semaphore(max_concurrent_copies)
    tasks = []
    for file_path in file_list:
        if os.path.exists(file_path):
            dst_path = os.path.join(dst_dir, os.path.basename(file_path))
            tasks.append(copy_file(file_path, dst_path, semaphore))

    await asyncio.gather(*tasks)


async def move_files(file_list, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    max_concurrent_copies = max_concurrent_copy_threads_algorithm(file_list, dst_dir)
    semaphore = asyncio.Semaphore(max_concurrent_copies)
    tasks = []
    for file_path in file_list:
        if os.path.exists(file_path):
            dst_path = os.path.join(dst_dir, os.path.basename(file_path))
            tasks.append(move_file(file_path, dst_path, semaphore))

    await asyncio.gather(*tasks)


# usage
file_list, dst_dir = read_file_list('filelist.txt')
if not (file_list and dst_dir):
    quit(-1)

# asyncio.run(copy_files(file_list, dst_dir))
asyncio.run(move_files(file_list, dst_dir))
