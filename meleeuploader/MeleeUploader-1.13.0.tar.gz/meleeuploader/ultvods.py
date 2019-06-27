#!/usr/bin/env python3

from consts import *
import pickle

queue = None
with open(queue_values, "rb") as f:
    queue = pickle.load(f)

for options in queue:
    options.file = "/Volumes/N240/Videos/" + options.file.split("/")[-1]

with open(queue_values, "wb") as f:
    f.write(pickle.dumps(queue))
