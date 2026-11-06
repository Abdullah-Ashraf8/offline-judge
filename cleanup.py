# cleanup.py - remove temporary build folders and Python caches
import atexit
import os
import shutil

import config


def remove_build_dir(build_dir):
    """Delete one build folder; a missing folder is fine."""
    shutil.rmtree(build_dir, ignore_errors=True)


def remove_empty_work_dir():
    """Remove work/ only when nothing is left in it."""
    try:
        os.rmdir(config.WORK_DIR)
    except OSError:
        pass


def remove_pycache():
    """Delete every __pycache__ folder under the project."""
    for root, dirs, _ in os.walk(config.BASE_DIR):
        if ".git" in dirs:
            dirs.remove(".git")
        for name in list(dirs):
            if name == "__pycache__":
                shutil.rmtree(os.path.join(root, name), ignore_errors=True)
                dirs.remove(name)


atexit.register(remove_pycache)
