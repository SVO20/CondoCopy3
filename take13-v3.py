"""
Module provides functionality to extract a compact datetime string from a various datetime formats.

includes the function to extract and validate datetime components from a string
and return a formatted compact datetime string.
"""

import re
from datetime import datetime
from typing import Optional

def extract_compact_datetime(dt_str: str) -> Optional[str]:
    # Regular expression pattern for datetime
    datetime_pattern = (
        r"(?P<year>20\d{2}|\d{2})"               # year
        r"([-/]?)"                               # first separator
        r"(?P<month>0[1-9]|1[0-2])"              # month
        r"([-/]?)"                               # second separator
        r"(?P<day>0[1-9]|[12]\d|3[01])"          # day
        r"([ Tt_])?"                             # date-time separator
        r"(?P<hour>[01]\d|2[0-3])?"              # hour
        r"([:.]?)"                               # hour-minute separator
        r"(?P<minute>[0-5]\d)?"                  # minute
        r"([:.]?)"                               # minute-second separator
        r"(?P<second>[0-5]\d)?"                  # second
    )

    match = re.match(datetime_pattern, dt_str)
    if not match:
        return None

    # Extract components from the matched groups
    components = match.groupdict()
    year = components.get('year')
    month = components.get('month')
    day = components.get('day')
    hour = components.get('hour', '00')
    minute = components.get('minute', '00')
    second = components.get('second', '00')

    # Check if mandatory components are None
    if year is None or month is None or day is None:
        return None

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
