#!/usr/bin/env python3

import os
import sys

import msgpack

def create_log(files):
    log = {}
    for filename in files:
        log[filename] = os.path.getmtime(filename)

    return log

def check_log(log, quickcheck=False):
    if quickcheck is False:
        changed = []
    for filename, logged_mtime in log.items():
        current_mtime = os.path.getmtime(filename)
        if current_mtime != logged_mtime:
            if quickcheck:
                return False

            else:
                changed.append(filename)
    if not quickcheck:
        return changed

def read_log(logfile, quickcheck=False):
    with open(logfile, "rb") as f:
        return check_log(msgpack.unpackb(f.read(), raw=False), quickcheck)

def write_log(logfile, filenames):
    with open(logfile, "wb") as f:
        f.write(msgpack.packb(create_log(filenames), use_bin_type=False))

if __name__=="__main__":
    if len(sys.argv) > 1:
        log = create_log(sys.argv[1:])
        write_log("mylog", log)

    else:
        log = read_log("mylog")
        print(check_log(log, quickcheck=True))

