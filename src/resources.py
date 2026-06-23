import sys
import os


def resource_path(relative):
    """Return an absolute path to a bundled resource.

    Works both when running from source and when frozen by PyInstaller,
    where data files are unpacked into the sys._MEIPASS temp directory.
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        # When running from source this file lives in src/, so the project
        # root (which contains ui/ and img/) is one level up.
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base, relative)
