"""
macOS convenience functions
"""

import platform
import sys

from vsutillib.process import RunCommand


def isMacDarkMode():
    """
    Test for macOS Mojave Dark Mode

    Returns:
        bool:

        True if the macOS is using Dark Mode

        False if not or if called on other operating systems
    """

    if platform.system() == "Darwin":
        cmd = RunCommand("defaults read -g AppleInterfaceStyle")

        if getattr(sys, 'frozen', False):
            # running in pyinstaller bundle dark mode does not apply
            return False

        if cmd.run():
            for e in cmd.output:
                if e.find("Dark") >= 0:
                    return True

    return False
