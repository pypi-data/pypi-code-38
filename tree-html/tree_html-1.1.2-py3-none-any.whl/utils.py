import os
import subprocess as sp


def run(cmd):
    """Calls subprocess using cmd and returns stdout"""
    out = sp.run(cmd, check=True, capture_output=True)
    return out.stdout


def remove_temp_files(files: list):
    if not isinstance(files, list):
        files = [files]

    [os.unlink(f) for f in files]
