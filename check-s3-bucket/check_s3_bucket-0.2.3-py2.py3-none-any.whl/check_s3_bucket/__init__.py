#!/usr/bin/env python
"""Check that a file was added to an S3 bucket in the given time window and is
of a reasonable size."""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import argparse
import datetime

try:
    import botocore.session
    import botocore.exceptions
except ImportError:
    print("Failed to import botocore.")
    exit(3)
try:
    import pytz
except ImportError:
    print("Failed to import pytz.")
    exit(3)

__version__ = "0.2.3"
NOW = datetime.datetime.now(pytz.utc)


def get_file_list(conn, bucket, prefix=""):
    """Return a list of files in the S3 bucket."""
    # I'm not concerened with the limitation of number of keys in the
    # response as the buckets have a lifecycle rule enabled and files are
    # automatically moved of the bucket.
    files = conn.list_objects_v2(Bucket=bucket, Prefix=prefix)["Contents"]
    files.sort(key=lambda x: x["LastModified"], reverse=True)
    files = files[:2]
    for file in files:
        file["HoursSinceLastModified"] = int(
            (NOW - file["LastModified"]).total_seconds() / 3600
        )
    return files


def main():
    """Main entrypoint."""

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bucket", help="S3 bucket to check")
    parser.add_argument(
        "prefix", help="Filter files by this prefix", nargs="?", default=""
    )
    parser.add_argument(
        "age_warning_threshold",
        help="""Warning threshold for the age of the latest file in hours
        (defaults to 24)""",
        default=24,
        type=int,
        nargs="?",
    )
    parser.add_argument(
        "age_critical_threshold",
        help="""Critical threshold for the age of the latest file in hours
        (defaults to 48)""",
        default=48,
        type=int,
        nargs="?",
    )
    parser.add_argument(
        "size_warning_threshold",
        help="""Warning threshold for the difference in size between the latest
        2 files in percents (default to 25)""",
        default=25,
        type=int,
        nargs="?",
    )
    parser.add_argument(
        "size_critical_threshold",
        help="""Critical threshold for the difference in size between the latest
        2 files in percents (default to 50)""",
        default=50,
        type=int,
        nargs="?",
    )
    args = parser.parse_args()

    # Connect to S3, get list of files.
    session = botocore.session.get_session()
    # pylint: disable=invalid-name
    s3 = session.create_client("s3")
    try:
        files = get_file_list(s3, args.bucket, args.prefix)
    except botocore.exceptions.BotoCoreError as exception:
        print("Failed to list the files in the S3 bucket.")
        print(str(exception))
        exit(3)

    if not files:
        print("Not matching files in bucket.")
        exit(2)

    # Calculate the age of the latest file and if it's in the thresholds set.
    if files[0]["LastModified"] > NOW:
        print("Latest file is from the future, something is wrong.")
        exit(3)
    timedelta = files[0]["HoursSinceLastModified"]
    if timedelta > args.age_critical_threshold:
        print(
            "Last file modified is older than {} hours.".format(
                args.age_critical_threshold
            )
        )
        exit(2)
    elif timedelta > args.age_warning_threshold:
        print(
            "Last file modified is older than {} hours.".format(
                args.age_warning_threshold
            )
        )
        exit(1)

    # Calculate the size ratio between the latest 2 files and check if
    # it's in the threshold set.
    if files[0]["Size"] == 0:
        print("Latest file is empty.")
        exit(2)
    elif len(files) == 1:
        print(
            """Found only 1 file in the bucket, can't calculate size
        difference."""
        )
        exit(3)
    elif files[1]["Size"] == 0:
        print("The last but 1 file is empty, can't calculate size difference.")
        exit(3)

    size_ratio = 100 * abs(
        (files[1]["Size"] - files[0]["Size"]) / files[1]["Size"]
    )
    if size_ratio > args.size_critical_threshold:
        print(
            "The size difference between the latest 2 file is {}%.".format(
                size_ratio
            )
        )
        exit(2)
    if size_ratio > args.size_warning_threshold:
        print(
            "The size difference between the latest 2 file is {}%.".format(
                size_ratio
            )
        )
        exit(1)
    else:
        print("File found and is within the thresholds set.")


if __name__ == "__main__":
    main()
