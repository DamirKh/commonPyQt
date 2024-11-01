import os
import pathlib

try:
    from version import rev, app_name
    _r = rev.split('.')
    if len(_r):
        major = _r[0]
    else:
        major = rev
except ImportError:
    rev = 'UNKNOWN'
    app_name = "Unknown_app"


def get_user_data_path():
    """Returns the user's data directory in an OS-independent way."""

    home_dir = pathlib.Path.home()
    app_data_dir = home_dir / "AppData" if os.name == "nt" else home_dir / ".config"
    user_data_dir = app_data_dir / f"{app_name}_{major}"

    return user_data_dir
