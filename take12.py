import os
from pymediainfo import MediaInfo
from datetime import datetime

from compact_datetime import dtstring_to_compactformat


def get_file_type(file_path) -> str:
    """Determine if the file is image, video, audio, or other type using MediaInfo

    :return: str  in  ( 'Image', 'Video', 'Audio', 'Other' )
    """
    minf = MediaInfo.parse(file_path)
    for track in minf.tracks:
        # Return first specific track found
        if track.track_type == "Image":
            return "Image"
        elif track.track_type == "Video":       # if not an image
            return "Video"
        elif track.track_type == "Audio":       # if not an image and not a video
            return "Audio"
    # Default
    return "Other"


def extract_key_datetime(file_path):
    """Extract key date/time from the metadata of image or video file, if available.
    Usually 'taken' or 'encoded' or 'modified' date/time

    :return  key date/time in if available in YYYYMMDD_HHMMSS compact_format, otherwise None
    """
    if not os.path.isfile(file_path):
        # print(f"The file {file_path} does not exist or is a directory.")
        return None

    try:
        file_type = get_file_type(file_path)
        media_info = MediaInfo.parse(file_path)
        #print(os.path.basename(file_path), f"   ----------->  ", file_type)

        for track in media_info.tracks:
            if file_type == "Image":
                # For images, look for EXIF 'Date/Time Original' or 'Encoded date' or similar tags

                # or track.file_last_modification_date
                if dt_information := track.other_date_taken or track.other_date_time_original or track.encoded_date :
                    print('dt_image_inf=', dt_information)
                    return dt_information
            elif file_type == "Video":
                # For videos, look for 'Encoded date' or similar tags
                # or track.file_last_modification_date
                if dt_information := track.encoded_date or track.tagged_date:
                    print('dt_video_inf=', dt_information)
                    return dt_information

    except Exception as e:
        print(f"An error occurred while processing the file {file_path}: {e}")
        raise
    # Default
    return None


def generate_new_filename(file_path):
    """Generates a new filename based on the taken date or last modification date.

    :param file_path: Path to the file
    :return: New filename
    """
    file_type = get_file_type(file_path)
    key_datetime = extract_key_datetime(file_path)
    compact_datetime = dtstring_to_compactformat(key_datetime)

    print(f"{file_type} --- {key_datetime} --- {compact_datetime}")

    original_filename = os.path.basename(file_path)
    name, ext = os.path.splitext(original_filename)

    if file_type in ["Image", "Video"]:
        if key_datetime:
            # compact_datetime used
            new_filename = f"{compact_datetime}_{name}{ext}"
            return new_filename
        else:
            # modified datetime used if  key_datetime  is None
            modif_time = os.path.getmtime(file_path)
            compact_datetime = dtstring_to_compactformat(modif_time)
            new_filename = f"{compact_datetime}-modif-{name}{ext}"
            return new_filename
    else:
        # Other files
        new_filename = f"{name}{ext}"

    return new_filename


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
