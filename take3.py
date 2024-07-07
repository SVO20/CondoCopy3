import os
import toml


def load_cameras_structures(file_path) -> dict:
    with open(file_path, 'r', encoding='utf-8') as file:
        return toml.load(file)


cameras_structures = load_cameras_structures("cameras.toml")


def analyze_SD_card(drive_path, cameras_structures):
    sd_card_dirs = []
    for root, dirs, files in os.walk(drive_path):
        for dir in dirs:
            rel_dir = os.path.relpath(os.path.join(root, dir), drive_path)
            sd_card_dirs.append(rel_dir.replace("\\", "/"))

    # Compare with known cameras directory structures
    for camera, info in cameras_structures['cameras'].items():
        if set(sd_card_dirs) == set(info['structure']):
            return camera
    return None


SD_path = 'G:/'
result = analyze_SD_card(SD_path, cameras_structures)

print(f"Структура SD карты соответствует: {result if result else '--'}")
