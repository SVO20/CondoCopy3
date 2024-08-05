from types import SimpleNamespace
import toml

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
    def __init__(self, file_path):
        self.file_path = file_path
        self.load_settings()

    def load_settings(self):
        with open(self.file_path, 'r') as file:
            self.settings = toml.load(file)
        self._settings_namespace = SimpleNamespace(**self.settings)

    def get(self, key, default=None):
        return getattr(self._settings_namespace, key, default)

    def set(self, key, value):
        setattr(self._settings_namespace, key, value)
        self.settings[key] = value
        self.save_settings()

    def save_settings(self):
        with open(self.file_path, 'w') as file:
            toml.dump(self.settings, file)

    @property
    def take(self):
        return self._settings_namespace


# TEST
if __name__ == "__main__":
    settings = Settings("settings.toml")

    # Accessing properties
    print("default_action:", settings.take.default_action)
    print("start_in_tray:", settings.take.start_in_tray)
    print("additional_extensions:", settings.take.additional_extensions)

    # Modifying a setting
    settings.set("default_action", "move")

    # Accessing modified property
    print("Modified default_action:", settings.take.default_action)

    # Accessing all properties again
    all_settings = settings.take
    print("All settings:", all_settings)

    # Examples of accessing individual properties
    print("rename:", all_settings.rename)
    print("rename_heuristic:", all_settings.rename_heuristic)
    print("clear_DCIM_aftermove:", all_settings.clear_DCIM_aftermove)
    print("paired_extensions:", all_settings.paired_extensions)
