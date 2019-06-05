import boto3
from aws_utils.response import ResponseObject


def upload_file(file, bucket, file_name, output_format=None, raise_exception=False):
    exception = None
    session = boto3.session.Session()
    s3 = session.resource('s3')
    exception = None
    try:
        s3.meta.client.upload_file(file, bucket, file_name)
    except Exception as e:
        print(e)
        exception = e
    finally:
        if raise_exception:
            raise exception
        return ResponseObject(exception=exception,
                              output_format=output_format).response()


def get_object(bucket, file_path, output_format=None, raise_exception=False):
    data = None
    exception = None
    full_response = None
    session = boto3.session.Session()
    s3 = session.resource('s3')
    try:
        full_response = s3.meta.client.get_object(Bucket=bucket, Key=file_path)
        data = full_response.get('Body').read().decode('utf-8')
    except Exception as e:
        print(e)
        exception = e
    finally:
        if raise_exception:
            raise exception
        return ResponseObject(data=data,
                              exception=exception,
                              output_format=output_format,
                              full_response=full_response).response()
