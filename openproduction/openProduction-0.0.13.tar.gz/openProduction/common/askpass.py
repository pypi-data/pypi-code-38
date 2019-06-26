#!/usr/bin/env python
#
# Short & sweet script for use with git clone and fetch credentials.
# Requires GIT_USERNAME and GIT_PASSWORD environment variables,
# intended to be called by Git via GIT_ASKPASS.
#

from sys import argv
from os import environ

if "USERNAME" in argv[1].upper():
    print (environ['GIT_USERNAME'])
    exit()

if "PASSWORD" in argv[1].upper():
    print (environ['GIT_PASSWORD'])
    exit()

exit(1)