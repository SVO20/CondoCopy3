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

    # First and Third separator pattern
    a_sep_pattern = r"([^\w\/|!?:<>\s]| )?"  # Matches one non-word character except '\/|!?:<>', or space, or empty
    # Second separator pattern, with 'T'
    b_sep_pattern = r"([^\w\/|!?:<>\s]|[Tt]| )?"  # Matches non-word character except '\/|!?:<>', or 'T', 't', or space


    full_pattern = (
            r"(.*)?" +  # Match any characters before the date-time
            year_pattern + a_sep_pattern +
            month_pattern + r"\2" +  # \2 ensures the same separator as between year and month
            day_pattern +

            b_sep_pattern +  # Separator between date and time

            hour_pattern + a_sep_pattern +
            minute_pattern + r"\7" +  # \7 ensures the same separator as between hour and minute
            second_pattern +
            r"(.*)?"  # Matches any characters after, greedy
    )

    match = re.match(full_pattern, dt_str)
    if not match:
        return None

    # Extract components from the matched groups
    groups = match.groups()
    year = groups[0]
    sep1 = groups[1]
    month = groups[2]
    day = groups[4]
    sep2 = groups[5]
    hour = groups[6]
    sep3 = groups[7]
    minute = groups[8]
    second = groups[10] if groups[10] else "00"

    # Check for invalid empty date-time separator when other separators are present
    if sep2 == "" and (sep1 or sep3):
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
