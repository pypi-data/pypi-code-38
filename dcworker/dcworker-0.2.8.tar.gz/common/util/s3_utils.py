import boto3
import os
from os import listdir
from os.path import isfile, join, isdir

def create_s3_client(s3_temp_token):
    client = boto3.client(
        's3',
        region_name=s3_temp_token["s3_region"],
        aws_access_key_id=s3_temp_token["access_key_id"],
        aws_secret_access_key=s3_temp_token["secret_access_key"],
        aws_session_token=s3_temp_token['session_token'])
    return client


def create_temp_s3_client(s3_temp_token):
    client = boto3.client(
        's3',
        region_name=s3_temp_token["s3_region"],
        aws_access_key_id=s3_temp_token["access_key_id"],
        aws_secret_access_key=s3_temp_token["secret_access_key"],
        aws_session_token=s3_temp_token['session_token'])
    return client


def upload_dir_to_s3(dir_path, bucket_name, folder_name, uuid, client):
    s3_folder_name = "{0}/{1}".format(uuid, folder_name)

    for f in listdir(dir_path):
        if isfile(join(dir_path, f)):
            print("uploading file {0} to {1}".format(join(dir_path, f), construct_s3_path(bucket_name, s3_folder_name)))
            upload_file_to_s3(join(dir_path, f), bucket_name, s3_folder_name, client)
        elif isdir(join(dir_path, f)):
            print("uploading directory {0} to {1}".format(join(dir_path, f), construct_s3_path(bucket_name, s3_folder_name)))
            s3_dir_name = folder_name + "/" + f
            upload_dir_to_s3(join(dir_path, f), bucket_name, s3_dir_name, uuid, client)

    return s3_folder_name


def upload_file_to_s3(file_path, bucket_name, folder_name, client):
    invalid_extension = [".c", ".cpp", ".js", ".java", ".exe", ".dll", ".o"]

    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        name, extension = os.path.splitext(filename)
        if extension not in invalid_extension:
            s3_file_name = "{0}/{1}".format(folder_name, filename)
            print("uploading file {0} to {1}".format(file_path, construct_s3_path(bucket_name, s3_file_name)))
            client.upload_file(file_path, bucket_name, s3_file_name)
            return s3_file_name
    else:
        raise ValueError("file {0} does not exist".format(file_path))


def construct_s3_path(bucket_name, folder_name):
    return "s3://{0}/{1}".format(bucket_name, folder_name)


def s3_path_join(path, *paths):
    for p in paths:
        path += "/" + p

    return path
