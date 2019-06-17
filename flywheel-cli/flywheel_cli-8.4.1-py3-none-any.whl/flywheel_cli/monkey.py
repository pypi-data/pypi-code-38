"""This module provides system-level monkey patches as needed"""

def patch_fs():
    """On windows, python 3.6.6 os.readlink errors if passed bytes instead of a string.

    This monkey-patch fixes the case where pyfilesystem uses fsencode before calling readlink.
    """
    import os
    if os.name == 'nt':
        from fs.osfs import OSFS

        def _gettarget(self, sys_path):
            try:
                target = os.readlink(os.fsdecode(sys_path))
            except OSError:
                return None
            else:
                return os.fsencode(target)

        OSFS._gettarget = _gettarget
