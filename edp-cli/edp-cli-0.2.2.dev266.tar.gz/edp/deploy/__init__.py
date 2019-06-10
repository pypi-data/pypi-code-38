import requests
import os
import pathlib
import json
from bson.objectid import ObjectId
import boto3
import click
from urllib.parse import urlparse


def extract_url(api_url, s3_bucket, s3_bucket_prefix, path):
    api_path = os.path.join(api_url, path)
    click.echo(click.style('Downloading: %s' % api_path, fg='green'))
    r = requests.get(api_path)

    s3_path = os.path.join(s3_bucket_prefix, path)
    click.echo(click.style('Uploading to S3: %s' % s3_path, fg='yellow'))
    s3_bucket.put_object(Key=s3_path, Body=r.content, ContentType='application/json')

    # Now extract any files we need to upload
    doc = r.json()
    if isinstance(doc, dict):
        extract_files(api_url, s3_bucket, s3_bucket_prefix, doc)

def upload_file(api_url, s3_bucket, s3_bucket_prefix, file_id):
    file_url = '%s/file/%s' % (api_url, file_id)
    file_download_url = '%s/download' % file_url
    click.echo(click.style('Downloading: %s' % file_download_url, fg='green'))
    r = requests.get(file_download_url, allow_redirects=False)

    s3_file_download_url_key = '%s/file/%s/download' % (s3_bucket_prefix, file_id)
    click.echo(click.style('Uploading to S3: %s' % s3_file_download_url_key, fg='yellow'))
    # Need to remove the presigned bit
    s3_url = r.headers['Location'].split('?')[0]
    s3_url = urlparse(s3_url).path
    s3_url = '/%s' % s3_url.split('/', 2)[2]
    s3_bucket.put_object(Key=s3_file_download_url_key, Body=b'',
                      WebsiteRedirectLocation=s3_url)

    click.echo(click.style('Downloading: %s' % file_url, fg='green'))
    r = requests.get(file_url)
    s3_file_url_key = '%s/file/%s' % (s3_bucket_prefix, file_id)
    click.echo(click.style('Uploading to S3: %s' % s3_file_url_key, fg='yellow'))
    s3_bucket.put_object(Key=s3_file_url_key, Body=r.content, ContentType='application/json')

def extract_files(api_url, s3_bucket, s3_bucket_prefix, item):
    for key in item:
        if key.endswith('FileId'):
            file_id = item[key]
            upload_file(api_url, s3_bucket, s3_bucket_prefix, file_id)

def extract_path(api_url, s3_bucket, s3_bucket_prefix, path, children):
    api_path = os.path.join(api_url, path)
    click.echo(click.style('Downloading: %s' % api_path, fg='green'))
    r = requests.get(api_path)

    s3_path = os.path.join(s3_bucket_prefix, path)
    click.echo(click.style('Uploading to S3: %s' % s3_path, fg='yellow'))
    s3_bucket.put_object(Key=s3_path, Body=r.content, ContentType='application/json')

    doc = r.json()
    if isinstance(doc, list):
        for item in doc:
            if '_id' in item:
                new_path = os.path.join(path, item['_id'])
                extract_path(api_url, s3_bucket, s3_bucket_prefix, new_path, children)
            extract_files(api_url, s3_bucket, s3_bucket_prefix, item)
    else:
        extract_files(api_url, s3_bucket, s3_bucket_prefix, doc)

    try:
        if ObjectId(os.path.basename(path)):
            extract_path(api_url, s3_bucket, s3_bucket_prefix,
                         os.path.join(path, children[0]), children[1:])
    except:
        pass

def extract_misc(api_url, s3_bucket, s3_bucket_prefix):
    extract_url(api_url, s3_bucket, s3_bucket_prefix, 'user/me')
    extract_url(api_url, s3_bucket, s3_bucket_prefix, 'edp/configuration')

    api_path = os.path.join(api_url, 'oauth/provider?redirect=dummy')
    click.echo(click.style('Downloading: %s' % api_path, fg='green'))
    r = requests.get(api_path)

    s3_path = os.path.join(s3_bucket_prefix, 'oauth/provider')
    click.echo(click.style('Uploading to S3: %s' % s3_path, fg='yellow'))
    s3_bucket.put_object(Key=s3_path, Body=r.content, ContentType='application/json')



def deploy(api_url, api_root, children, s3_bucket, s3_bucket_prefix):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket)
    s3_bucket_prefix = '%s%s' % (s3_bucket_prefix, urlparse(api_url).path)
    extract_path(api_url, bucket, s3_bucket_prefix, api_root, children)
    extract_misc(api_url, bucket, s3_bucket_prefix)
