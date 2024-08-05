"""
Module provides functionality to match dir structure with camera model

"""
from collections import Counter
from typing import Optional
import numpy as np
from my_utils import get_directories


def match_camera_model(sd_path, cameras: dict) -> Optional[str]:
    """Matches the SD card structure to a camera model"""
    def _calculate_weights(cameras_data) -> dict[str, float]:
        """Calculate token weights based on their frequency in  cameras_data  """
        all_tokens = [token
                      for item in cameras_data.values()
                      for token in item['structure']]
        token_counts = Counter(all_tokens)
        token_weights = {token: 1 / count for token, count in token_counts.items()}
        return token_weights

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
    base_weights = _calculate_weights(cameras)
    additional_weights = _calculate_weights(relevant_models)

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


