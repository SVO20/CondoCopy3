"""
Module provides functionality to extract a compact datetime string from a various datetime formats.

includes the function to extract and validate datetime components from a string
and return a formatted compact datetime string.
"""

import re
from datetime import datetime
from typing import Optional


def extract_compact_datetime(dt_str: str) -> Optional[str]:
    # Regular expression patterns for datetime components
    year_pattern = r"(20\d{2}|\d{2})"  # Matches either YYYY or YY
    month_pattern = r"(0[1-9]|1[0-2])"  # Matches MM (01-12)
    day_pattern = r"(0[1-9]|[12]\d|3[01])"  # Matches DD (01-31)
    hour_pattern = r"([01]\d|2[0-3])"  # Matches HH (00-23)
    minute_pattern = r"([0-5]\d)"  # Matches MM (00-59)
    second_pattern = r"([0-5]\d)?"  # Matches SS (00-59) or nothing

    # Separator patterns
    sep1_pattern = r"([_\sTt\W])?"  # Matches '_', ' ', 'T', 't', or any non-word character
    sep2_pattern = r"([_\sTt\W])?"  # Matches '_', ' ', 'T', 't', or any non-word character
    sep3_pattern = r"([_\sTt\W])?"  # Matches '_', ' ', 'T', 't', or any non-word character

    # Full pattern with optional file extension
    full_pattern = (
        r".*" +  # Match any characters before the date-time
        year_pattern + sep1_pattern +
        month_pattern + sep1_pattern +
        day_pattern + sep2_pattern +
        hour_pattern + sep3_pattern +
        minute_pattern + sep3_pattern +
        second_pattern +
        r".*?(\.[a-zA-Z0-9]{1,20})?$"  # Match optional file extension up to 20 characters
    )

    match = re.match(full_pattern, dt_str)
    if not match:
        return None

    # Extract components from the matched groups
    groups = match.groups()
    year = groups[0]
    month = groups[2]
    day = groups[4]
    hour = groups[6]
    minute = groups[8]
    second = groups[10] if groups[10] else "00"

    # Adjust the year if it's in YY format
    if len(year) == 2:
        year = "20" + year

    # Validate the extracted date-time components
    try:
        datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    except ValueError:
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
