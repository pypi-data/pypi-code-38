#!/usr/bin/env python

import osxmetadata
from osxmetadata import *

print(osxmetadata.__file__)

md = OSXMetaData("/Users/rhet/Dropbox (Personal)/Code/osxmetadata/osxmetadata/t.py")
md.tags.update("test", "foo")
print("tags = ", md.tags)
print(md.tags)
for tag in md.tags:
    print("got a tag: ", tag)

print(md.tags)
