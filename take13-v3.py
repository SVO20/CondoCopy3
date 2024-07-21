"""
Module provides functionality to extract a compact datetime string from a filename

"""
import os.path
import re
from datetime import datetime
from typing import Optional


def extract_compact_datetime(str_filename: str) -> Optional[str]:
    # Extract filename without extention
    dt_str, _ = os.path.splitext(os.path.basename(str_filename))

    # Regular expression pattern for datetime
    datetime_pattern = (
        r"(.*?)"
        r"(?P<year>20\d{2}|\d{2})"               # year
        r"(?P<sep1>[^\w\|!?<>\s]|[ _])?"         # separator
        r"(?P<month>0[1-9]|1[0-2])"              # month
        r"(?P<sep2>[^\w\|!?<>\s]|[ _])?"         # separator
        r"(?P<day>0[1-9]|[12]\d|3[01])"          # day
        r"(?P<sep3>[-Tt_ ])?"                    # date-time separator
        r"(?P<hour>[01]\d|2[0-3])?"              # hour
        r"(?P<sep4>[^\w\/|!?<>\s]|[:._ ])?"      # hour-minute separator
        r"(?P<minute>[0-5]\d)?"                  # minute
        r"(?P<sep5>[^\w\/|!?<>\s]|[:._ ])?"      # minute-second separator
        r"(?P<second>[0-5]\d)?"                  # second
    )

    match = re.match(datetime_pattern, dt_str)
    if not match:
        return None

    # Extract components from the matched groups
    components = match.groupdict()
    year = components.get('year')
    sep1 = components.get('sep1')
    month = components.get('month')
    sep2 = components.get('sep2')
    day = components.get('day')
    sep3 = components.get('sep3')
    hour = components.get('hour')
    sep4 = components.get('sep4')
    minute = components.get('minute')
    sep5 = components.get('sep5')
    second = components.get('second') if components.get('second') is not None else '00'

    # Check separators rules
    if not sep1 == sep2 or not (sep4 == sep5 or not sep5):
        return None
    if sep3 == '' != sep2 or sep3 == '' != sep4:
        return None

    # Check if mandatory components are None
    if year is None or month is None or day is None:
        return None

    # Adjust the year if it's in YY format
    if len(year) == 2:
        year = "20" + year

    # Validate the extracted date-time components
    try:
        datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    except (ValueError, TypeError):
        return None

    # Return the formatted date-time string
    return f"{year}{month}{day}_{hour}{minute}{second}"


def load_test_data(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

def test_extract_compact_datetime():
    test_data = load_test_data("extractor_test_data.txt")
    print(f"{'Original String':<40}{'Extracted Datetime':<40}")
    print("="*80)
    for test_case in test_data:
        result = extract_compact_datetime(test_case)
        result_str = result if result is not None else "None"
        print(f"{test_case:<40}{result_str:<40}")

test_extract_compact_datetime()
