import os

import toml

# Load the contents of the uploaded TOML file
file_path = 'cameras.toml'
with open(file_path, 'r') as file:
    camera_data = toml.load(file)

def get_directories(path):
    """Get a list of all directories in the given path."""
    directories = []
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            directories.append(os.path.relpath(os.path.join(root, dir_name), path))
    return directories


def match_camera_model(sd_path, camera_data):
    """Match the SD card structure to a camera model."""
    sd_directories = get_directories(sd_path)
    camera_models = camera_data['cameras']

    # Sort camera models by the length of their required structure in descending order
    sorted_models = sorted(camera_models.items(), key=lambda item: len(item[1]['structure']),
                           reverse=True)
    print(sorted_models)
    for model, data in sorted_models:
        required_structure = set(data['structure'])
        if required_structure.issubset(sd_directories):
            return model
    return None


# Example usage
sd_path = 'g://'  # Change this to the actual path of the SD card
camera_model = match_camera_model(sd_path, camera_data)
print(f"The SD card is matched with: {camera_model}")
