from sys import version_info, stderr

# Require python 3.6
required_major = 3
required_minor = 6

if version_info.major < required_major or version_info.minor < required_minor:
    stderr.write('\nPython error: mekpie requires python version 3.6 or later!\n')
    exit(1)

from .core import main

# Program entry point for module
if __name__ == "__main__":
    main()