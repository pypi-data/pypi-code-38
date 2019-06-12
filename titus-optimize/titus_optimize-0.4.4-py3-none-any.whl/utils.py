import time
import os
import subprocess
import sys
import tempfile


def s3cp(src_path, dest_path, num_retries=3, quiet=True):
    num_tries = 0
    backoff_time_sec = 0.2
    src_path = src_path.replace("s3n://", "s3://")
    dest_path = dest_path.replace("s3n://", "s3://")
    args = ["aws", "s3", "cp"]
    if quiet:
        args.append("--quiet")
    args.extend([src_path, dest_path])
    while num_tries < 3:
        ret = subprocess.call(args)
        if ret != 0:
            num_tries += 1
            time.sleep(backoff_time_sec)
            backoff_time_sec *= 2
        else:
            break
    if ret != 0:
        raise Exception("Failed to copy %s to %s." % (src_path, dest_path))
