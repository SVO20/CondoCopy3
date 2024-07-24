import os

import toml

from logger import debug, error, info, omit, success, trace, warning


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
        error(f"File not found: {toml_filename}")
        raise FileNotFoundError(f"{toml_filename} does not exist")

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


d_cameras = load_cameras('cameras.toml')
success("'cameras.toml' loaded successfully.")
