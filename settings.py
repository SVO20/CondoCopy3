import os
from types import SimpleNamespace

import toml

from logger import debug, error, info, omit, success, trace, warning
from my_utils import expand_compressed


DEFAULT_SETTINGS = (
    b'eJx1jj0LwjAURff+ipC5dHB3kOrgUAQHHaSER/NiA/koyYvUf29qIYjo9u4958GNBIGEdoICPNmWKTAR'
    b'K4kKkiEBA2nvcs2tfyCvAjqwWLQ1ihFT0JH0UABIqZdPMAJnQhfzHTO9Ma4lrxmfpzuv+2oCHVB+O9lq'
    b'2vNm8ZrZmizW7253vn52fTUYhCD27bEToAjDMrJsWKGnEUP8gVUyRkAib4HyBOvlX9adLofCXkszZ/I=')

DEFAULT_CAMERAS = (
    b'eJyFklFr2zAUhd/9Ky7OywZrHbaxQmEPrp12htgOUQgrJRhNvq4FtpRdySn995OStU2JQ58kjnTP/c6V'
    b'JrBqpQGhVSMfB+JWagWN7NBLlktlIGykekTaklTWhKAbYCkITjUYS4OwA6GBRhPsOEk9ODPeI3ETBBMv'
    b'99xeBxO3f/ivXyb7tVJu2Tj91QV+wkOYJlkefoEwz1gSbgAmcAGdNNb33XLbGrAaakkorCbpOtuWW+gH'
    b'd+MPwtaxoHKXldPxFfQT8c5F26EvZukFaW0/n4X6ekq1WGbreDWL4nXyK41u0nwdJfNskRW3nnXkdDGP'
    b'7+cZW7kIPgHh38Ex957Nj8rDHVgF+mQcROuG7bcKjcX6OGIQvFBu3raXTKvnKr76tgnGB/gClX9fluVq'
    b'jzsi382K2TKeH5+wsrgPjzslXGlVzUp2rlUSF2WR+/c6qVroJyTWalvdXf0+V79/62OfN5rwNHK3bXn1'
    b'YzqdfmR3NlCsatKyrlLcSYFjNtHhO+xd5OGLR0wQojIui/F6qp9Up3n9znnN6blyBreV0L37rqOIruAf'
    b'sT0aYg==')


class Settings:
    def __init__(self, file_path_to_load, default_bytes_const=DEFAULT_SETTINGS):
        self._file_path = file_path_to_load
        if not os.path.exists(self._file_path):
            with open(self._file_path, 'w') as file:
                default_settings_str = expand_compressed(default_bytes_const)
                file.write(default_settings_str)
        with open(self._file_path, 'r') as file:
            self._settings = toml.load(file)

        self._settings_namespace = SimpleNamespace(**self._settings)

    def get(self, key, default=None):
        return getattr(self._settings_namespace, key, default)

    def set(self, key, value):
        setattr(self._settings_namespace, key, value)
        self._settings[key] = value
        self.rewrite_settings()

    def rewrite_settings(self):
        with open(self._file_path, 'w') as file:
            toml.dump(self._settings, file)

    @property
    def take(self):
        return self._settings_namespace


def load_cameras(toml_filename) -> dict:
    """Load and validate cameras' "footprints" from a .toml file"""

    def ensure_pathlist(inlist: list) -> list:
        try:
            return [os.path.relpath(item) for item in inlist]
        except TypeError as e:
            error(f"TypeError in ensure_pathlist: {e}. Ensure all items are strings.")
            raise
        except ValueError as e:
            error(f"ValueError in ensure_pathlist: {e}. Invalid path provided.")
            raise

    if not os.path.exists(toml_filename):
        with open(toml_filename, 'w') as file:
            default_settings_str = expand_compressed(DEFAULT_CAMERAS)
            file.write(default_settings_str)

    try:
        with open(toml_filename, 'r') as file:
            d_cams = toml.load(file)['cameras']
            info(f"Successfully loaded cameras from {toml_filename}")
            return {cam_name: {'structure': ensure_pathlist(d_cams.get(cam_name)['structure'])} for
                    cam_name in d_cams}
    except KeyError as e:
        error(f"Key error: {e}")
        raise
    except (TypeError, ValueError) as e:
        error(f"Bad pathname in .toml encountered: {e}")
        raise
    except toml.TomlDecodeError as e:
        error(f"Error decoding TOML file: {e}")
        raise


def load_settings(toml_filename) -> Settings:
    """Load app settings from a .toml file"""

    success(f"'{toml_filename}' loaded successfully.")
    return Settings("settings.toml")
