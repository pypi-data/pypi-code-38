# -*- coding:utf-8 -*-

from urllib.parse import quote
import logging
import os
import requests
import json
import uuid

_logger = logging.getLogger(__name__)


# ------------------------------------ General function ------------------------------------

def get_absolute_path(relative_path):
    """
    :param relative_path: relative path of the file to the current directory of auto.py file
    :return:
    """
    # current directory path that contain this file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return "{0}/{1}".format(dir_path, relative_path)


def encode_string(url):
    return quote(url, safe='')


# ------------------------------------ Github API ----------------------------------------

def create_release(repo_info, release_info):
    """
    Create a new release and return release_id.
    Reference: https://developer.github.com/v3/repos/releases/#create-a-release
    :param repo_info: (type:dict)
        repo_owner: (type:str)
        repo_name: (type:str)
    :param release_info: (type: dict)
        tag_name: (type:str)
        target_commitish: (type:str)
        name: (type:str)
        body: (type:str)
    :return: created release id
    """
    url = "https://api.github.com/repos/{repo_owner}/{repo_name}/releases".format(
        repo_owner=repo_info.get('repo_owner'),
        repo_name=repo_info.get('repo_name')
    )
    headers = {"Authorization": "token {token}".format(token=repo_info.get('access_token'))}
    try:
        resp = requests.post(url, json=release_info, headers=headers)
        return json.loads(resp.content)
    except Exception as e:
        _logger.error(e)
        return False


def get_release_by_tag_name(repo_info, tag_name):
    url = "https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag_name}".format(
        repo_owner=repo_info.get('repo_owner'),
        repo_name=repo_info.get('repo_name'),
        tag_name=tag_name
    )
    headers = {"Authorization": "token {token}".format(token=repo_info.get('access_token'))}
    try:
        resp = requests.get(url, headers=headers)
        return json.loads(resp.content)
    except Exception as e:
        _logger.error(e)
    return False


def delete_release_by_tag_name(repo_info, tag_name):
    """
    Delete release and the tag it was attached to
    """
    release = get_release_by_tag_name(repo_info, tag_name)
    url = "https://api.github.com/repos/{repo_owner}/{repo_name}/releases/{release_id}".format(
        repo_owner=repo_info.get('repo_owner'),
        repo_name=repo_info.get('repo_name'),
        release_id=release.get('id')
    )
    headers = {"Authorization": "token {token}".format(token=repo_info.get('access_token'))}
    try:
        resp = requests.delete(url, headers=headers)
        delete_tag(repo_info, tag_name)
        return json.loads(resp.content)
    except Exception as e:
        _logger.error(e)
    return False


def upload_assets(repo_info, release_info, asset_info):
    """
    Reference: https://developer.github.com/v3/repos/releases/#upload-a-release-asset
    :param repo_info: *(type:dict)
        repo_owner: *(type:str)
        repo_name: *(type:str)
    :param release_info: (*type:dict)
        upload_url: *(type:str)
    :param asset_info: *(type:dict)
        name: *(type:str) asset file name
        local_path: *(type:str) path to the asset file on local machine
        label: (type:str)
    """
    upload_url = release_info.get('upload_url')
    upload_url = upload_url.replace('{?name,label}', '?name={name}&label={label}'.format(
        name=encode_string(asset_info.get('name')),
        label=encode_string(asset_info.get('label') or '')
    ))
    headers = {"Authorization": "token {token}".format(token=repo_info.get('access_token'))}
    files = {'file': open(asset_info.get('local_path'), 'rb')}
    try:
        resp = requests.post(upload_url, headers=headers, files=files)
        return json.loads(resp.content)
    except Exception as e:
        _logger.error(e)
    return False


def delete_tag(repo_info, tag_name):
    """
    Tag deleted --> release attached to this tag will be delete
    Reference: https://developer.github.com/v3/git/refs/#delete-a-reference
    :param repo_info: (type:dict) like param in function create_release()
    :param tag_name: (type:str)
    """
    url = "https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs/tags/{tag_name}".format(
        repo_owner=repo_info.get('repo_owner'),
        repo_name=repo_info.get('repo_name'),
        tag_name=tag_name
    )
    headers = {"Authorization": "token {token}".format(token=repo_info.get('access_token'))}
    try:
        resp = requests.delete(url, headers=headers)
        if resp.status_code == 204:
            return True
    except Exception as e:
        _logger.error(e)
    return False


# ------------------------------------ Build packages ----------------------------------------

# ------- Prepare bash scripts ---------

def update_install_prerequisite_script(unique_str):
    """
    :return: path to the updated install prerequisite script
    """
    raw_install_script_path = get_absolute_path('data/raw_install_prerequisite.sh')
    install_script_path = '/tmp/%s_install_prerequisite.sh' % unique_str
    local_user = os.environ.get('USER') or os.environ.get('HOME').split('/')[-1]

    with open(raw_install_script_path) as f:
        content = f.read()
        content = content.replace('<username>', local_user)

    with open(install_script_path, 'w') as f:
        f.write(content)

    return install_script_path


def update_build_package_script_path(repo_info, unique_str):
    """
    :param repo_info: *(type:dict)
        repo_name: *(type:str)
        repo_owner: *(type:str)
        tag_name: *(type:str)
        access_token: *(type:str)
    :param unique_str:
    :return:
    """
    package_file_name = '{tag_name}.tar.gz'.format(
        repo_name=repo_info.get('repo_name'),
        tag_name=repo_info.get('tag_name')
    )
    raw_build_script_path = get_absolute_path('data/raw_build_package.sh')
    build_script_path = '/tmp/%s_build_package.sh' % unique_str

    with open(raw_build_script_path, 'r') as f:
        content = f.read()
        content_keys = {
            "<package_file_name>": package_file_name,
            "<repo_owner>": repo_info.get('repo_owner'),
            "<repo_name>": repo_info.get('repo_name'),
            "<tag_name>": repo_info.get('tag_name'),
            "<access_token>": repo_info.get('access_token'),
            "<unique_str>": unique_str
        }
        for key in content_keys:
            content = content.replace(key, content_keys.get(key))

    with open(build_script_path, 'w') as f:
        f.write(content)

    return build_script_path


def build_package(repo_info):
    """
    Build pwa-pos package on local machine
    :param repo_info: (type:dict)
        + repo_name
        + repo_owner
        + tag_name
        + access_token
    :return: path to built package file on the local machine if build process success, else ''
    """
    unique_str = str(uuid.uuid4())
    install_script_path = update_install_prerequisite_script(unique_str)
    build_script_path = update_build_package_script_path(repo_info, unique_str)
    os.system('sudo bash %s > /dev/null' % install_script_path)
    os.system('rm -rf %s' % install_script_path)

    # give 3 times for build package, if failed, return empty path
    retry = 2
    built_status = os.system('bash %s > /dev/null' % build_script_path)
    while built_status != 0 and retry > 0:
        built_status = os.system('bash %s > /dev/null' % build_script_path)
        retry -= 1
    if built_status != 0:
        return ''

    os.system('rm -rf %s' % build_script_path)

    built_package_file_name = '{repo_name}-{tag_name}.tar.gz'.format(
        repo_name=repo_info.get('repo_name'),
        tag_name=repo_info.get('tag_name')
    )
    built_package_path = '/tmp/%s/%s' % (unique_str, built_package_file_name)
    return built_package_path
