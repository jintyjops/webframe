"""Utilities for interacting with the storage directory."""

import os
from webframe.core import app

def store(data, folder=None, file=None, binary=False):
    """Store data in file in folder."""
    if not folder_exists(folder):
        make_folder(folder)

    with open(path(folder, file), 'w' + ('b' if binary else '')) as f:
        f.write(data)

def get(data, folder=None, file=None, binary=False):
    """Get data from a file."""
    with open(path(folder, file), 'r' + ('b' if binary else '')) as f:
        return f.read()

def folder_exists(folder):
    """Determine if top level storage folder exists."""
    return os.path.exists(path(folder)) and os.path.isdir(path(folder))

def make_folder(folder):
    """Create a folder in the storage directory."""
    os.mkdir(path(folder))

def delete(folder=None, file=None):
    if folder is None and file is None:
        raise ValueError('You must specify at least one of file or folder.')
    os.remove(path(folder, file))

def path(folder=None, _file=None):
    """Get the main storage folder."""
    p = f'{app.userapp.settings.STORAGE_DIR}'
    if folder is not None:
        p += '/' + folder
    if _file is not None:
        p += '/' + _file
    return p
