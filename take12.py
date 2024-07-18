import os
from pymediainfo import MediaInfo
from datetime import datetime


def get_file_type(file_path) -> str:
    """Determine if the file is image, video, or other type using MediaInfo

    :return: str  in  ( 'Image', 'Video', 'Other' )
    """
    minf = MediaInfo.parse(file_path)
    for track in minf.tracks:
        # Return first specific track found
        if track.track_type == "Image":
            return "Image"
        elif track.track_type == "Video":
            return "Video"
    # Place for additional analyze logic
    # Default
    return "Other"


def extract_key_datetime(file_path, file_type: str = 'Other'):
    """Extract key date/time from the metadata of image or video file, if available.
    Usually 'taken' or 'encoded' or 'modified' date/time

    :return  key date/time in if available, otherwise None
    """
    if not os.path.isfile(file_path):
        print(f"The file {file_path} does not exist or is a directory.")
        return None, "Other"

    file_type = get_file_type(file_path)
    print(f"----------->  ", file_path, file_type)
    try:
        media_info = MediaInfo.parse(file_path)
        for track in media_info.tracks:
            if file_type == "Image":
                # For images, look for EXIF 'Date/Time Original' or similar tags
                date = track.other_date_taken or track.other_date_time_original or track.encoded_date
                if date:
                    return date[0], "Image"  # Return the first available date
            elif file_type == "Video":
                # For videos, look for 'Encoded date' or similar tags
                date = track.encoded_date or track.tagged_date or track.file_last_modification_date
                if date:
                    return date, "Video"
    except Exception as e:
        print(f"An error occurred while processing the file {file_path}: {e}")
        raise
    return None, file_type


def generate_new_filename(file_path):
    """Generates a new filename based on the taken date or last modification date.

    :param file_path: Path to the file
    :return: New filename
    """
    taken_date, file_type = extract_key_datetime(file_path)
    dir_name, original_filename = os.path.split(file_path)
    name, ext = os.path.splitext(original_filename)

    if file_type in ["Image", "Video"]:
        if taken_date:
            # Remove milliseconds and timezone if present
            taken_date = taken_date.split('.')[0]
            try:
                if 'T' in taken_date:
                    # ISO 8601 datetime format
                    date_str = datetime.strptime(taken_date, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d_%H%M%S')
                else:
                    # Regular datetime format
                    date_str = datetime.strptime(taken_date, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d_%H%M%S')
                new_filename = f"{date_str}_{name}{ext}"
            except ValueError:
                # Handle case where the date does not contain time
                print(f"Invalid taken date (no time): {taken_date}, using modification date instead.")
                mod_time = os.path.getmtime(file_path)
                date_str = datetime.fromtimestamp(mod_time).strftime('%Y%m%d_%H%M%S')
                new_filename = f"{date_str}-modif-{name}{ext}"
        else:
            mod_time = os.path.getmtime(file_path)
            date_str = datetime.fromtimestamp(mod_time).strftime('%Y%m%d_%H%M%S')
            new_filename = f"{date_str}-modif-{name}{ext}"
    else:
        new_filename = f"placeholder_{name}{ext}"

    return os.path.join(dir_name, new_filename)


def analyze_directory(directory):
    print(f"{'Original Filename':<90} {'New Filename':<90}")
    print(f"{'-'*90} {'-'*90}")
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            new_filename = generate_new_filename(file_path)
            print(f"{filename:<90} {os.path.basename(new_filename):<90}")


if __name__ == "__main__":
    directory = 'testfiles'
    analyze_directory(directory)
