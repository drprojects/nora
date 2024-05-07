import os
import shutil


__all__ = ['cleanup']


def cleanup(root):
    """Clean the pesky folders created by some libraries.
    """
    for dirname in ['data', 'logs', 'outputs']:
        path = os.path.join(root, dirname)
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
