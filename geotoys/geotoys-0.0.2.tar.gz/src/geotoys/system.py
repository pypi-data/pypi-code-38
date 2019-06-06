"""
Module containing methods for working with system environment and objects, e.g. files
"""

def list_ext(path, ext):
    """
    Recursively list all files under path with given extension
    """
    from glob import glob
    import os

    if not ext.startswith('.'):
        ext = f".{ext}"

    return sorted(glob(os.path.join(path, f"**/*{ext}"), recursive=True))


def list_dirs(path, suffix):
    """
    Recursively list all dirs under path with given suffix
    """
    import os

    dirs = list()
    for p in os.listdir(path):
        p = os.path.join(path, p)
        if os.path.isdir(p):
            if p.endswith(suffix):
                dirs.append(p)
            else:
                dirs += list_dirs(p, suffix)
    return dirs
