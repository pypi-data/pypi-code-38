#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from requests.auth import HTTPBasicAuth
from goss.app.logger import Logger
import json
import requests
import base64
import time
import os
import configparser
import sys
import mimetypes

logger = Logger()

API_URL = 'https://api.github.com{}'
ACCEPT = 'application/vnd.github.v3+json'

class BaseObject(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        return json.loads(self.to_json())

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def __str__(self):
        return self.to_json()

class Content(BaseObject):
    pass

class Author():
    def __init__(self, name, email):
        self.name = name
        self.email = email

class Response(BaseObject):
    def __init__(self):
        self.contents = []
    pass

class Github():
    debug = False
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def set_author(self, name, email):
        self.author = Author(name, email)

    def set_owner(self, owner):
        self.owner = owner

    def set_debug(self, debug: bool):
        self.debug = debug

    def get_user_info(self):
        '''
        获取用户信息
        '''
        url = '/user'
        self._request('get', url)
        return self.response.status_code, self.response.json()

    def get_release(self):
        return Release(self)

    def get_file(self, owner, repository, path, ref='master'):
        '''
        获取文件
        https://developer.github.com/v3/repos/contents/#get-contents
        '''
        url = '/repos/{}/{}/contents/{}'.format(owner, repository, path)
        self._request('get', url, ref=ref)
        #  is_success = self.response.status_code == 200
        return self.response.status_code, self.response.json()

    def get_file_blob(self, owner, repository, sha, ref='master'):
        '''
        获取文件内容，超过 1 MB 时
        https://developer.github.com/v3/git/blobs/#get-a-blob
        '''
        url = '/repos/{}/{}/git/blobs/{}'.format(owner, repository, sha)
        self._request('get', url, ref=ref)
        return self.response.status_code, self.response.json()

    def delete_file(self, owner, repository, path, sha, branch='master'):
        '''
        删除文件
        https://developer.github.com/v3/repos/contents/#delete-a-file
        '''
        url = '/repos/{}/{}/contents/{}'.format(owner, repository, path)
        data = {
            "message": "Delete {}".format(path),
            "committer": {
                "name": self.author.name,
                "email": self.author.email
                },
            "sha": sha,
            "branch": branch
        }
        self._request('delete', url, **data)
        return self.response.status_code, self.response.json()

    def create_file_from_url(self, owner, repository, url, path=None, sha=None):
        '''
        从 url 创建文件
        '''
        res = requests.get(url)
        byte_data = res.content

        return self._create_file(owner, repository, url, byte_data, path, sha)

    def create_file_from_path(self, owner, repository, filepath, path=None, sha=None):
        '''
        从本地创建文件
        https://developer.github.com/v3/repos/contents/#create-a-file
        '''
        byte_data = None
        with open(filepath, 'rb') as f:
            byte_data = f.read()
            f.close()
        return self._create_file(owner, repository, filepath, byte_data, path, sha)

    def _create_file(self, owner, repository, filepath, byte_data,
            path = None, sha=None):
        '''
        创建文件
        https://developer.github.com/v3/repos/contents/#create-a-file
        '''
        if not path:
            path = os.path.basename(filepath)
        content = base64.b64encode(byte_data).decode()
        url = '/repos/{}/{}/contents/{}'.format(owner, repository, path)
        data = {
            "message": "Create file {}".format(path),
            "author": {
                "name": self.author.name,
                "email": self.author.email
                },
            "content": content
            }
        if sha:
            data['sha'] = sha
        self._request('put', url, **data)
        return self.response.status_code, self.response.json()

    def create_repository(self, name, description="", homepage="",
            private=False, has_issues = True, has_projects = True,
            has_wiki = True, **kw
        ):
        '''
        创建仓库 https://developer.github.com/v3/repos/#create
        '''
        all_args = locals()
        url = '/user/repos'
        all_args.pop('self')
        self._request('post', url, **all_args)
        return self.response.status_code, self.response.json()

    def create_organization_repository(self, organization, name,
            description="", homepage="", private=False, has_issues = True,
            has_projects = True, has_wiki = True, **kw
        ):
        '''
        创建组织仓库 https://developer.github.com/v3/repos/#create
        '''
        all_args = locals()
        url = '/orgs/{}/repos'.format(organization)
        all_args.pop('self')
        self._request('post', url, **all_args)
        success = self.response.status_code == 201
        return success, self.response.json()

    def delete_repository(self, owner, repo):
        '''
        删除 repository
        https://developer.github.com/v3/repos/#delete-a-repository
        '''
        url = '/repos/{}/{}'.format(owner, repo)
        self._request('delete', url)
        code = self.response.status_code
        return code, self.response.json() if code != 204 else None

    def get_owner_repositorys(self):
        '''
        获取当前用户的 repository 列表
        https://developer.github.com/v3/repos/#list-your-repositories
        '''
        url = '/user/repos'
        self._request('get', url)
        return self.response.status_code, self.response.json()

    def get_repository(self, owner, repo):
        '''
        获取 repository 详情
        https://developer.github.com/v3/repos/#get
        '''
        url = '/repos/{}/{}'.format(owner, repo)
        self._request('get', url)
        return self.response.status_code, self.response.json()

    def _request(self, method, url, **kw):
        data = {}
        if method in ('put', 'post', 'delete'):
            data['json'] = kw
        elif method in ('get'):
            data['params'] = kw

        req_data = dict(
            method = method,
            url = API_URL.format(url),
            headers={"Accept": ACCEPT},
            auth=HTTPBasicAuth(self.user, self.password),
        )
        if data:
            req_data.update(data)
        res = requests.request(**req_data)
        self.response = res
        if self.debug:
            logger.debug("Response code {}".format(res.status_code))
            if res.status_code != 204:
                logger.debug("Response data\n{}".format(
                    json.dumps(self.response.json(), indent=4)))

class Release(Github):
    def __init__(self, github, *args, **kwargs):
        self.github = github

    def create_release(self,owner, repo, tag_name, name="", body="",
            draft=False, prerelease=False, target_commitish='master'):
        '''
        创建 release
        https://developer.github.com/v3/repos/releases/#create-a-release
        '''
        if not body:
            body = 'Create by [goss](https://github.com/wxnacy/goss)'
        all_args = locals()
        all_args.pop('owner')
        all_args.pop('repo')
        all_args.pop('self')
        url = f'/repos/{owner}/{repo}/releases'
        self.github._request('post', url, **all_args)
        return self.github.response.status_code, self.github.response.json()

    def get_release(self, owner, repo, release_id):
        '''
        Get a single release
        https://developer.github.com/v3/repos/releases/#get-a-single-release
        '''
        url = f'/repos/{owner}/{repo}/releases/{release_id}'
        self.github._request('get', url)
        return self.github.response.status_code, self.github.response.json()

    def get_release_by_tag(self, owner, repo, tag_name):
        '''
        Get a release by tag name
        https://developer.github.com/v3/repos/releases/#get-a-release-by-tag-name
        '''
        url = f'/repos/{owner}/{repo}/releases/tags/{tag_name}'
        self.github._request('get', url)
        return self.github.response.status_code, self.github.response.json()

    def get_latest_release(self, owner, repo):
        '''
        Get the latest release
        https://developer.github.com/v3/repos/releases/#get-the-latest-release
        '''
        url = f'/repos/{owner}/{repo}/releases/latest'
        self.github._request('get', url)
        return self.github.response.status_code, self.github.response.json()

    def get_releases(self, owner, repo):
        '''
        List releases for a repository
        https://developer.github.com/v3/repos/releases/#list-releases-for-a-repository
        '''
        url = f'/repos/{owner}/{repo}/releases'
        self.github._request('get', url)
        return self.github.response.status_code, self.github.response.json()

    def delete_release(self, owner, repo, release_id):
        '''
        Delete a release
        https://developer.github.com/v3/repos/releases/#delete-a-release
        '''
        url = f'/repos/{owner}/{repo}/releases/{release_id}'
        self.github._request('delete', url)
        data = None
        if self.github.response.status_code != 204:
            data = self.github.response.json()
        return self.github.response.status_code, data

    def get_assets(self, owner, repo, release_id):
        '''
        List releases for a repository
        https://developer.github.com/v3/repos/releases/#list-releases-for-a-repository
        '''
        url = f'/repos/{owner}/{repo}/releases/{release_id}/assets'
        self.github._request('get', url)
        return self.github.response.status_code, self.github.response.json()

    def get_asset(self, owner, repo, asset_id):
        '''
        Get a single release asset
        https://developer.github.com/v3/repos/releases/#get-a-single-release-asset
        '''
        url = f'/repos/{owner}/{repo}/releases/assets/{asset_id}'
        self.github._request('get', url)
        return self.github.response.status_code, self.github.response.json()

    def delete_asset(self, owner, repo, asset_id):
        '''
        Delete a release asset
        https://developer.github.com/v3/repos/releases/#delete-a-release-asset
        '''
        url = f'/repos/{owner}/{repo}/releases/assets/{asset_id}'
        self.github._request('delete', url)
        data = None
        if self.github.response.status_code != 204:
            data = self.github.response.json()
        return self.github.response.status_code, data

    def upload_asset_from_path(self, owner, repo, release_id, path, name='',
            label=''):
        '''
        创建 asset
        https://developer.github.com/v3/repos/releases/#upload-a-release-asset
        '''
        if not name:
            name = os.path.basename(path)
        url = f'https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets?name={name}&label={label}'
        data = open(path, 'rb').read()
        content_type = mimetypes.guess_type(path)[0]
        req_data = dict(
            method = 'POST',
            data = data,
            url = url,
            headers={"Accept": ACCEPT, "Content-Type": content_type},
            auth=HTTPBasicAuth(self.github.user, self.github.password),
        )
        res = requests.request(**req_data)
        return res.status_code, res.json()


if __name__ == "__main__":
    config_path = '{}/.config/gos/config'.format(os.getenv("HOME"))
    credential_path = '{}/.config/gos/credentials'.format(os.getenv("HOME"))

    credential = configparser.ConfigParser()
    credential.read(credential_path)
    default_cred = credential['default']

    g = Github(default_cred['user'], default_cred['password'])
    g.debug =True

    config = configparser.ConfigParser()
    config.read(config_path)
    author = config['user']
    g.set_author(author['name'], author['email'])

    owner = config['repository']['owner']
    repo = config['repository']['repo']
    #  g.create_from_file('image', '/Users/wxnacy/Downloads/mac-font2.png',
            #  'common/{}'.format(time.time()))

    #  g.create_repository('test2')
    #  g.create_organization_repository(, 'test3')
    #  g.get_file('wxnacy', 'image', 'push')
    #  g.get_owner_repositorys()

    #  g.upload_release_asset()

    r = Release(g)
    code, msg = r.get_releases('wxnacy', 'test')
    r1 = r.upload_asset_from_path('wxnacy', 'test', msg[0]['id'],
            '/Users/wxnacy/Downloads/404-1.png', '', '')
    #  print(r.create_release('wxnacy', 'test', 'v1.0.2' ))
    #  print(r.get_release_by_tag('wxnacy', 'test', 'v1.0.0'))
    #  print(r.get_release_by_id('wxnacy', 'test', 17763761))
    #  code, msg = r.get_assets('wxnacy', 'test', 17763761)
    #  print(r.get_asset('wxnacy', 'test', 13013362))
    #  print(r.delete_asset('wxnacy', 'test', msg[0]['id']))
    #  print(r.get_latest_release('wxnacy', 'test'))
    #  print(r1)
    #  r.delete_release('wxnacy', 'test', msg[0]['id'])

    #  code, msg = r.get_assets('wxnacy', 'test', 17763761)
