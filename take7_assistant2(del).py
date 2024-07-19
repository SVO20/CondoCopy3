"""
Development and testing stand for the copy/move function.

This script deletes specified files from two disks.
"""


import os


filelist_path = "filelist.txt"

# Function to read and split file paths and the path to the second disk
def read_file_list(filelist_path):
    with open(filelist_path, 'r') as f:
        lines = f.readlines()
    files_to_delete = lines[:-1]
    disk2 = lines[-1].strip()
    return files_to_delete, disk2

# Function to extract the base path from the first file path in the list
def extract_base_path(file_path):
    return os.path.dirname(file_path)

if os.path.exists(filelist_path):
    files_to_delete, disk2 = read_file_list(filelist_path)

    if files_to_delete:
        base_path = extract_base_path(files_to_delete[0].strip())

    # Deleting files
    for file in files_to_delete:
        file_path = file.strip()
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

        # Deleting file from the second disk
        disk2_file_path = file_path.replace(base_path, disk2)
        if os.path.exists(disk2_file_path):
            os.remove(disk2_file_path)
            print(f"Deleted file from the second disk: {disk2_file_path}")

    print("All files successfully deleted.")
    os.remove(filelist_path)
    print(f"{os.path.basename(filelist_path)} successfully deleted.")
else:
    print(f"File {filelist_path} not found.")
