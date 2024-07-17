import wmi


def get_removable_disk_info(drive_letter):
    try:
        # WMI object
        c = wmi.WMI()

        for disk in c.Win32_LogicalDisk():
            if True or disk.DeviceID.upper() == drive_letter.upper():
                # disk information
                print(f"Drive: {disk.DeviceID}")
                print(f"Type: {disk.Description}")
                print(f"File System: {disk.FileSystem}")
                print(f"Free Space: {disk.FreeSpace}")
                print(f"Total Size: {disk.Size}")
                print(f"Drive Type: {disk.DriveType}")
                print(f"Serial Number: {disk.VolumeSerialNumber}")
                print(f"Volume Name: {disk.VolumeName}")
                return


        print(f"Removable {drive_letter}: not found.")

    except Exception as e:
        print(f"Error: {e}")



get_removable_disk_info('G:')