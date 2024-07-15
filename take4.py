from typing import Optional
import toml
import os
from collections import Counter
import numpy as np


def load_cameras(toml_filename) -> dict:
    """Load and validate cameras' "footprints" from  .toml file"""
    def ensure_pathlist(inlist: list) -> list:
        return [os.path.relpath(item) for item in inlist]

    with open(toml_filename, 'r') as file:
        try:
            d_cams = toml.load(file)['cameras']
            return {cam_name: {'structure': ensure_pathlist(d_cams.get(cam_name)['structure'])}
                    for cam_name in d_cams}
        except KeyError:
            # exception log
            raise
        except (TypeError, ValueError):
            # encountered bad pathname in  .toml
            raise


def get_directories(start_path) -> list:
    """Get a list of related directories for the given path"""
    apath = os.path.abspath(start_path)
    rel_directories = []
    for root, dirs, files in os.walk(apath):
        for dir_name in dirs:
            # append relative path from abs path "root + dir_name" that started from  apath
            rel_directories.append(os.path.relpath(os.path.join(root, dir_name), apath))
    return rel_directories


def calculate_weights(cameras_data) -> dict[str, float]:
    """Calculate token weights based on their frequency in  cameras_data  """
    all_tokens = [token
                  for item in cameras_data.values()
                  for token in item['structure']]
    token_counts = Counter(all_tokens)
    token_weights = {token: 1 / count for token, count in token_counts.items()}
    return token_weights


def match_camera_model(sd_path, cameras: dict) -> Optional[str]:
    """Matches the SD card structure to a camera model"""
    s_sd_directories = set(get_directories(sd_path))

    # Filtering camera models that have all directories present on the given SD card
    relevant_models = {}
    for model, data in cameras.items():
        if set(data['structure']).issubset(s_sd_directories):
            relevant_models[model] = data

    print(relevant_models)
    if not relevant_models:
        return None

    # Tokenization and calculation of base and additional weights
    base_weights = calculate_weights(cameras)
    additional_weights = calculate_weights(relevant_models)

    # Calculate resulting weights as the sum of base and additional weights
    resulting_weights = {token: base_weights.get(token, 0) + additional_weights.get(token, 0)
                         for token in additional_weights}

    # Vectorization of camera models using resulting weights
    model_vectors = {}
    for model, data in relevant_models.items():
        vector = np.array([resulting_weights[dir] for dir in data['structure']])
        model_vectors[model] = vector

    # Sorting models by specifity/complexity (token weights)
    sorted_models = sorted(relevant_models.items(),
                           key=lambda item: np.sum(model_vectors[item[0]]), reverse=True)

    # Return the first camera model (with the highest complexity)
    return sorted_models[0][0] if sorted_models else None


# usage
sd_path = "g:"  # actual path of the SD card
d_cameras = load_cameras('cameras.toml')

camera_model = match_camera_model(sd_path, d_cameras)
print(f"The SD card is matched with: {camera_model}")
