# About Date and Time Formats in Filenames

## Overview

The format `YYYYMMDD_HHMMSS` is a variation of ISO 8601, commonly used as a convention for naming files on Android devices. This format includes the year, month, day, hour, minute, and second without timezone offsets and milliseconds. It uses an underscore to separate the date and time components, making it widely adopted among smartphone manufacturers for filesystem compatibility.

## Example

A typical filename using this format might look like:

`20230718_143045.jpg`

Where:
- `2023` is the year
- `07` is the month
- `18` is the day
- `14` is the hour
- `30` is the minute
- `45` is the second

## Usage

This naming convention is widely used for:
- Photograph files
- Video files
- Other media files

It is primarily used to ensure the sorting of a large number of files using system tools without the need for third-party systems. It allows you to accurately determine when a particular material was captured on an imaginary timeline just by looking at the list of files in Explorer, regardless of how extensive it is.


## Usage in CondoCopy3 App

This format will be used by the CondoCopy3 app to rename files obtained from SD cards and devices. The date and time will be placed at the **beginning** of the filename to facilitate sorting. After the date and time, any separator such as '_', '--', '--modif--' (for cases where the date and time of capture are unknown, but the last modification time is available), etc., can be used. Following the separator, any user-defined or original filename (as it was on the device) can be included.

### Examples

- `20230718_143045_DSC8967.JPEG`
- `20230718_143045-taken-img4563.RAW`
- `20230718_143045--modif--some_image.TIFF`
- `20230718_143049.jpg`
- `20230718_143049(1).jpg`
- `20230718_143049(2).jpg`         (<-- three images that have been shot at the same second)
- `20230718_150000--modif--holiday_photo.PNG`
- `20230718_151030_custom_name.MOV`
- `20230718_153015-user_image.BMP`

