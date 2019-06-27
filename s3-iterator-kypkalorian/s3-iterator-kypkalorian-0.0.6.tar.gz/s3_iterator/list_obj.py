import boto3


def list_obj(bucket):

    client = boto3.client('s3')

    response = client.list_objects(
        Bucket=bucket,
        Delimiter='|',
        #MaxKeys=1000,
    )
    return response


def list_obj_marker(bucket, nextMarker):

    client = boto3.client('s3')

    response = client.list_objects(
        Bucket=bucket,
        Delimiter='|',
        Marker=nextMarker,
        MaxKeys=1000,
    )
    return response


def list_prefix(bucket, prefix):

    client = boto3.client('s3')

    response = client.list_objects(
        Bucket=bucket,
        Delimiter='|',
        MaxKeys=1000,
        Prefix=prefix,
    )
    return response


def list_prefix_marker(bucket, nextMarker, prefix):

    client = boto3.client('s3')

    response = client.list_objects(
        Bucket=bucket,
        Delimiter='|',
        Marker=nextMarker,
        MaxKeys=1000,
        Prefix=prefix,
    )
    return response
