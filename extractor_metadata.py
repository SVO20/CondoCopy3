"""
Module provides analyzing media files (images and videos) by extracting key metadata
and generating new filenames based on the metadata.

includes the functions to determine file type, extract key date/time from metadata,
and generate new filenames with compact date/time format as a prefix.
"""

import os
from pymediainfo import MediaInfo
from datetime import datetime
import piexif

from my_utils import dtstring_to_compactformat


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
    Usually 'taken', 'encoded', or 'modified' date/time

    :return: Key date/time in YYYYMMDD_HHMMSS compact format, otherwise None
    """
    if not os.path.isfile(file_path):
        # The file does not exist or is a directory
        return None

    try:
        file_type = get_file_type(file_path)
        media_info = MediaInfo.parse(file_path)
        #print(os.path.basename(file_path), f"   ----------->  ", file_type)

        if file_type == "Image":
            # Try to extract EXIF data using piexif
            try:
                exif_dict = piexif.load(file_path)
                dt_original = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
                dt_digitized = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeDigitized)
                dt_taken = dt_original or dt_digitized
                if dt_taken:
                    #print('exif_inf=', dt_taken.decode('utf-8'))
                    return dt_taken.decode('utf-8')
            except (piexif.InvalidImageDataError, KeyError):
                pass  # Format is not supported by piexif or no EXIF data found

            # If piexif fails or no EXIF data, use  MediaInfo
            for track in media_info.tracks:
                if dt_information := track.other_date_taken or track.other_date_time_original or track.encoded_date:
                    #print('dt_image_inf=', dt_information)
                    return dt_information[0] if isinstance(dt_information, list) else dt_information


        elif file_type == "Video":
            # For videos, look for 'Encoded date' or similar tags
            # or track.file_last_modification_date
            for track in media_info.tracks:
                if dt_information := track.encoded_date or track.tagged_date:
                    #print('dt_video_inf=', dt_information)
                    return dt_information[0] if isinstance(dt_information, list) else dt_information


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

    #print(f"{file_type} --- {key_datetime} --- {compact_datetime}")

    original_filename = os.path.basename(file_path)

    if file_type in ["Image", "Video"]:
        if key_datetime is not None:
            if original_filename.startswith(key_datetime):
                # no renaming needed if filename already starts with EXACT key_datetime
                return original_filename
            else:
                # compact_datetime added as prefix
                return f"{compact_datetime}_{original_filename}"
        else:
            # 'modified' datetime used if  key_datetime  is None
            modif_time = os.path.getmtime(file_path)
            compact_datetime = dtstring_to_compactformat(modif_time)
            # compact_datetime added as prefix
            return f"{compact_datetime}_{original_filename}"
    else:
        # Other files
        return original_filename


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
