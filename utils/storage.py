"""Utilities for interacting with the storage directory."""

import os, stat
import shutil
from webframe.core import app

def store(data, folder=None, _file=None, binary=False, permissions=stat.S_IRWXU):
    """Store data in file in folder."""
    if not folder_exists(folder):
        make_folder(folder)

    with open(path(folder, _file), 'w' + ('b' if binary else '')) as f:
        f.write(data)
    
    os.chmod(path(folder, _file), permissions)

def get(data, folder=None, _file=None, binary=False):
    """Get data from a file."""
    with open(path(folder, _file), 'r' + ('b' if binary else '')) as f:
        return f.read()

def exists(folder=None, _file=None):
    p = path(folder, _file)
    return os.path.exists(p) and os.path.isfile(p)

def folder_exists(folder):
    """Determine if top level storage folder exists."""
    return os.path.exists(path(folder)) and os.path.isdir(path(folder))

def make_folder(folder):
    """Create a folder in the storage directory."""
    os.mkdir(path(folder))

def delete(folder=None, _file=None):
    if folder is None and _file is None:
        raise ValueError('You must specify at least one of _file or folder.')
    os.remove(path(folder, _file))

def delete_folder(folder):
    p = path(folder)
    # os.chmod(p, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    deletetree(p)

def deletetree(folder):
    paths = [f for f in os.walk(folder)]
    paths.reverse()

    for path in paths:
        for f in path[2]:
            p = os.path.join(path[0], f)
            os.chmod(p, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            os.remove(p)
        for d in path[1]:
            p = os.path.join(path[0], d)
            os.chmod(p, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            os.rmdir(p)
    os.rmdir(folder)

def path(folder=None, _file=None):
    """Get the main storage folder."""
    p = f'{app.userapp.settings.STORAGE_DIR}'
    if folder is not None:
        p += '/' + folder
    if _file is not None:
        p += '/' + _file
    return p
