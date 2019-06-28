import boto3
import botocore
import cray.config as config
import json


def file_exists(bucket, file):
    s3 = boto3.resource("s3")
    try:
        s3.Object(bucket, file).load()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
    return True


def load_file(bucket, file):
    s3 = boto3.resource("s3")
    content_object = s3.Object(config.bucket(), file)
    return content_object.get()["Body"].read().decode("utf-8")


def load_json(bucket, file):
    f = load_file(bucket, file)
    return json.loads(f)


def list_subdirectories(bucket, prefix):
    paginator = boto3.client("s3").get_paginator("list_objects")
    folders = []
    iterator = paginator.paginate(
        Bucket=bucket, Prefix=prefix, Delimiter="/", PaginationConfig={"PageSize": None}
    )
    for response_data in iterator:
        prefixes = response_data.get("CommonPrefixes", [])
        for prefix in prefixes:
            prefix_name = prefix["Prefix"]
            if prefix_name.endswith("/"):
                folders.append(prefix_name.rstrip("/"))
    return folders


def list_all_files(bucket, prefix):
    s3 = boto3.client("s3")
    s3_result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/")

    if "Contents" not in s3_result:
        return []

    file_list = []
    for key in s3_result["Contents"]:
        file_list.append(key["Key"])

    while s3_result["IsTruncated"]:
        continuation_key = s3_result["NextContinuationToken"]
        s3_result = s3.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            Delimiter="/",
            ContinuationToken=continuation_key,
        )
        for key in s3_result["Contents"]:
            file_list.append(key["Key"])
    return file_list


def count_files(bucket, prefix):
    f = list_all_files(bucket, prefix)
    return len(f)


def last_modified(bucket, key):
    s3 = boto3.client("s3")
    o = s3.head_object(Bucket=bucket, Key=key)
    return o["LastModified"]
