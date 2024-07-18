from datetime import datetime, timedelta
from typing import Optional


def dtstring_to_compactformat(date, utc: int = 3) -> Optional[str]:
    """/GPT-assisted/
    Convert various date-time formats to compact standard YYYYMMDD_HHMMSS format.

    :param date: The date-time string to be converted.
    :param utc: Time shift (poisitive or negative)
    :return: The date-time string in YYYYMMDD_HHMMSS format or None if conversion is not possible.
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",       # Example: 2023-07-18 14:30:45 (ISO 8601)
        "%Y-%m-%d %H:%M",          # Example: 2023-07-18 14:30 (ISO 8601 without seconds)
        "%Y/%m/%d %H:%M:%S",       # Example: 2023/07/18 14:30:45
        "%Y/%m/%d %H:%M",          # Example: 2023/07/18 14:30
        "%d-%m-%Y %H:%M:%S",       # Example: 18-07-2023 14:30:45 (European format)
        "%d-%m-%Y %H:%M",          # Example: 18-07-2023 14:30 (European format without seconds)
        "%d/%m/%Y %H:%M:%S",       # Example: 18/07/2023 14:30:45 (European format)
        "%d/%m/%Y %H:%M",          # Example: 18/07/2023 14:30 (European format without seconds)
        "%m/%d/%Y %H:%M:%S",       # Example: 07/18/2023 14:30:45 (US format)
        "%m/%d/%Y %H:%M",          # Example: 07/18/2023 14:30 (US format without seconds)
        "%Y%m%d_%H%M%S",           # Example: 20230718_143045 (Compact format with separator)
        "%Y%m%d%H%M%S",            # Example: 20230718143045 (Compact format without separator)
        "%Y%m%d %H%M%S",           # Example: 20230718 143045 (Compact format with space separator)
        "%Y%m%d-%H%M%S",           # Example: 20230718-143045 (Compact format with dash separator)
        "%Y%m%d.%H%M%S",           # Example: 20230718.143045 (Compact format with dot separator)
        "%Y:%m:%d %H:%M:%S",       # Example: 2023:07:18 14:30:45 (Exif format)
        "%Y:%m:%d %H:%M",          # Example: 2023:07:18 14:30 (Exif format without seconds)
        "%d %b %Y %H:%M:%S",       # Example: 18 Jul 2023 14:30:45 (Verbose date format)
        "%d %b %Y %H:%M",          # Example: 18 Jul 2023 14:30 (Verbose date format without seconds)
        "%b %d, %Y %H:%M:%S",      # Example: Jul 18, 2023 14:30:45 (Verbose date format)
        "%b %d, %Y %H:%M",         # Example: Jul 18, 2023 14:30 (Verbose date format without seconds)
        "%Y.%m.%d %H:%M:%S",       # Example: 2023.07.18 14:30:45 (Dot-separated format)
        "%Y.%m.%d %H:%M",          # Example: 2023.07.18 14:30 (Dot-separated format without seconds)
        "%d.%m.%Y %H:%M:%S",       # Example: 18.07.2023 14:30:45 (Dot-separated European format)
        "%d.%m.%Y %H:%M",          # Example: 18.07.2023 14:30 (Dot-separated European format without seconds)
        "%Y%m%d %H%M",             # Example: 20230718 1430 (Compact format with space separator without seconds)
        "%Y%m%d_%H%M",             # Example: 20230718_1430 (Compact format with separator without seconds)
        "%Y%m%d-%H%M",             # Example: 20230718-1430 (Compact format with dash separator without seconds)
        "%Y%m%d.%H%M",             # Example: 20230718.1430 (Compact format with dot separator without seconds)
        "%Y-%m-%dT%H:%M:%S.%fZ",   # Example: 2023-07-18T14:30:45.123Z (ISO 8601 with milliseconds and Zulu time)
        "%Y-%m-%dT%H:%M:%S.%f%z",  # Example: 2023-07-18T14:30:45.123+0200 (ISO 8601 with milliseconds and UTC offset)
        "%Y-%m-%dT%H:%M:%S%z",     # Example: 2023-07-18T14:30:45+0200 (ISO 8601 with UTC offset)
        "%Y-%m-%dT%H:%M.%fZ",      # Example: 2023-07-18T14:30.123Z (ISO 8601 with milliseconds without seconds and Zulu time)
        "%Y-%m-%dT%H:%M.%f%z",     # Example: 2023-07-18T14:30.123+0200 (ISO 8601 with milliseconds without seconds and UTC offset)
        "%Y-%m-%dT%H:%M%z",        # Example: 2023-07-18T14:30+0200 (ISO 8601 without seconds and UTC offset)
        "%Y-%m-%d %H:%M:%S.%f",    # Example: 2023-07-18 14:30:45.123 (Date with milliseconds)
        "%Y-%m-%d %H:%M.%f",       # Example: 2023-07-18 14:30.123 (Date with milliseconds without seconds)
        "%Y%m%dT%H%M%SZ",          # Example: 20230718T143045Z (Compact ISO 8601 with Zulu time)
        "%Y%m%dT%H%M%S%z",         # Example: 20230718T143045+0200 (Compact ISO 8601 with UTC offset)
        "%Y%m%dT%H%MZ",            # Example: 20230718T1430Z (Compact ISO 8601 without seconds and Zulu time)
        "%Y%m%dT%H%M%z"            # Example: 20230718T1430+0200 (Compact ISO 8601 without seconds and UTC offset)
    ]
    is_utc_time = str(date).find("UTC") != -1
    if is_utc_time:
        delta = timedelta(hours=utc)
    else:
        delta = timedelta(hours=0)

    # Check if the date is a float, which might represent a UNIX timestamp
    if isinstance(date, float):
        try:
            # Convert UNIX timestamp to datetime
            dt = datetime.utcfromtimestamp(date)
            # Apply the UTC offset
            dt += timedelta(hours=utc)
            return dt.strftime("%Y%m%d_%H%M%S")
        except Exception as e:
            return None  # Return None if conversion fails

    date = str(date)

    print(f"OK {date=}")
    for fmt in formats:
        try:
            # Try to parse the date string with the current format
            dt = datetime.strptime(date, fmt)
            dt = dt + delta

            if '%S' in fmt:
                # normal
                return dt.strftime("%Y%m%d_%H%M%S")
            else:
                # If the format does not include seconds, add "00" for seconds
                return dt.strftime("%Y%m%d_%H%M00")

        except ValueError:
            # If parsing fails, continue to the next format
            continue

    return None  # Return None if no formats matched

