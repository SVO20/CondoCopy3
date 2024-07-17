"""
Development and testing stand of the copy/move function.

Creating files.
"""

import os
import random


def create_file(path, size_mb):
    """Create a file of a given size"""
    with open(path, 'wb') as f:
        f.write(os.urandom(size_mb * 1024 * 1024))


def save_file_list(filelist, filelist_filepath, disk2):
    """Save filelist and disk2 to the  filelist_filepath  file"""
    with open(filelist_filepath, 'w') as f:
        for file in filelist:
            f.write(file + '\n')
        f.write(disk2 + '\n')

#  ===================================================


disk1 = "g:"  # first disk
disk2 = "c:"  # second disk
filelist_filepath = "filelist.txt"
filelist = []

# Creating files on the first disk
for i in range(10):
    file_path = os.path.join(disk1, f"file_{i+1}_1-15MB.dat")
    create_file(file_path, random.randint(1, 15))
    filelist.append(file_path)
    print(f"{file_path} written successfully!")

for i in range(10):
    file_path = os.path.join(disk1, f"file_{i+1}_10-40MB.dat")
    create_file(file_path, random.randint(10, 40))
    filelist.append(file_path)
    print(f"{file_path} written successfully!")

for i in range(2):
    file_path = os.path.join(disk1, f"file_{i+1}_1-3GB.dat")
    create_file(file_path, random.randint(1024, 3072))
    filelist.append(file_path)
    print(f"{file_path} written successfully!")

# Save the list of files and the path to the second disk in a file
save_file_list(filelist, filelist_filepath, disk2)

print(f"File list saved in {filelist_filepath}")
