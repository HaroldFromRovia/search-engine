import os


def init_folders(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def touch_file(path):
    if not os.path.isfile(path):
        with open(path, 'w'): pass