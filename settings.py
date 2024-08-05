import os
from types import SimpleNamespace

import toml

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
    def __init__(self, file_path, default_bytes_const=DEFAULT_SETTINGS):
        self._file_path = file_path
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
