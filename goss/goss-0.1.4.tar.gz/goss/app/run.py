#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import click
from goss import Github
from goss import __version__
from goss.app import utils
from goss.app.config import goss_config
from goss.app.logger import Logger
import configparser
import os
import pyperclip
import json
import base64
import requests

GOSS_CONFIG_HOME = '{}/.config/goss'.format(os.getenv("HOME"))
GOSS_CONFIG_PATH = '{}/config'.format(GOSS_CONFIG_HOME)
GOSS_CREDENTIAL_PATH = '{}/credentials'.format(GOSS_CONFIG_HOME)
GOSS_USER_INFO_PATH = '{}/user.json'.format(GOSS_CONFIG_HOME)

logger = Logger()

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__.__version__)
    ctx.exit()

@click.group()
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show the version')
@click.option('--debug', '-d', is_flag=True, default=False, help='Run in debug')
@click.pass_context
def run(ctx, debug):
    '''
    Github Object Storage System
    '''
    if not os.path.exists(GOSS_CONFIG_HOME):
        os.mkdir(GOSS_CONFIG_HOME)
    if os.path.exists(GOSS_CREDENTIAL_PATH):
        cred = configparser.ConfigParser()
        cred.read(GOSS_CREDENTIAL_PATH)
        secs = cred.sections()
        if 'default' in secs:
            default_cred = cred['default']
            user = default_cred['user']
            password = default_cred['password']

            g = Github(user, password)
            g.set_owner(default_cred['owner'])

            conf = configparser.ConfigParser()
            conf.read(GOSS_CONFIG_PATH)
            author = conf['user']
            g.set_author(author['name'], author['email'])
            g.set_debug(debug)
            ctx.obj = g

def init_credentials_path():
    if not os.path.exists(GOSS_CONFIG_HOME):
        os.mkdir(GOSS_CONFIG_HOME)


@run.command(help='Log in to the github account')
@click.option('--user', '-u', prompt='Your Github user', help = 'Your Github user')
@click.option('--password', '-p', prompt='Your Github password',
        help = 'Your Github password',hide_input=True)
@click.option('--yes', '-y', is_flag = True, default = False, help = 'All questions answered yes')
@click.pass_context
def login(ctx, user, password, yes):
    g = ctx.obj
    confirm = utils.make_error_msg('The login information already exists. Do you want to replace it?')
    if not yes:
        if g and not click.confirm(confirm):
            return
    conf = configparser.ConfigParser()
    conf['default'] = dict(user = user, password = password)

    g = Github(user, password)
    code, data = g.get_user_info()
    if code != 200:
        utils.print_failed()
        logger.error('用户名或密码错误')
        return

    owner = data.get("name")
    conf['default']['owner'] = owner
    with open(GOSS_CREDENTIAL_PATH, 'w') as f:
        conf.write(f)
    with open(GOSS_USER_INFO_PATH, 'w') as f:
        f.write(json.dumps(data, indent = 4))
        f.flush()
        f.close()

    conf_data = dict(name = owner)
    email = data.get("email")
    if email:
        conf_data['email'] = email

    utils.config(GOSS_CONFIG_PATH, 'user', **conf_data)

    utils.print_success()
    logger.info('Name  :', owner)
    logger.info('Email :', email)

LARGE_SIZE = 1 * 1024 * 1024
TOO_LARGE_SIZE = 100 * 1024 * 1024


@run.command()
@click.option('--method', '-m', default = 'GET',
    help = 'GET/POST/PUT/DELETE for repository. Default is GET')
@click.option('--orga', '-o', help = 'If want create organization repository. Is required')
@click.option('--download', '-D', is_flag = True, help = 'Download file')
@click.option('--yes', '-y', is_flag = True, default = False, help = 'All questions answered yes')
@click.option('--output', '-O', help = 'Download name. Default is file name')
@click.option('--repo', '-r', required = True, help = 'Repository name')
@click.argument('path', default="/")
@click.pass_context
def file(ctx, repo, path, orga, method, download, output, yes):
    '''
    Get/Delete/Download your file

    If you want to upload file. Please use command

        goss <filepath> --repo=<repository-name>

    More usage see : goss --help
    '''
    g = ctx.obj
    if not g:
        click.echo('You have not logged in yet, please run goss-cli to login')
        ctx.exit()

    owner = orga if orga else g.owner

    def _get_progress(progress, total):
        '''打印进度条'''
        progress_ratio = progress / total
        progress_len = 20
        progress_num = int(progress_ratio * 20)
        pro_text = '[{:-<20s}] {:.2f}% {} / {}'.format(
            '=' * progress_num, progress_ratio * 100, progress, total)
        return pro_text


    def _save(p, filepath, content):
        '''保存文件'''
        byte_data = base64.b64decode(content.encode())
        _save_by_bytes(p, filepath, byte_data)

    def _save_by_bytes(p, filepath, byte_data):
        '''保存文件'''
        filedir = os.path.dirname(filepath)
        filename = os.path.dirname(filepath)
        with open(name, 'wb') as f:
            total = len(byte_data)
            progress = 0
            step = 10
            while progress < total:
                b = progress
                e = b + step
                f.write(byte_data[b:e])
                progress += step
                end = '\r'
                if progress >= total:
                    end = '\n'
                    progress = total
                print(p, _get_progress(progress, total), end = end)
            f.flush()
            f.close()

    if download:
        logger.info('Download file')
        logger.info('Owner\t: {}'.format(owner))
        logger.info('Repo\t: {}'.format(repo))
        logger.info('Path\t: {}'.format(path))
        logger.info('Waiting...')
        code, data = g.get_file(owner, repo, path)
        if code == 403:         # 文件太大，需要使用其它方式进行下载
            logger.warn('The file is larger than 1 MB and needs to be downloaded using the download_url.')
            path_dir = os.path.dirname(path)
            if not path_dir:
                path_dir = '/'
            c, files = g.get_file(owner, repo, path_dir)
            down_url = ''
            file_name = []
            for f in files:
                if f['path'] == path:
                    down_url = f['download_url']
                    file_name = f['name']
            file_res = requests.get(down_url)

            name = output or file_name
            _save_by_bytes(path, name, file_res.content)
            utils.print_success()
            ctx.exit()

        if code != 200:         # 其他错误直接返回
            utils.print_failed()
            logger.error(data.get("message"))
            ctx.exit()
        type = data.get("type")
        name = output or data.get("name")
        if isinstance(data, dict):
            content = data.get("content")
            _save(path, name, content)
        elif isinstance(data, list):
            pass
        utils.print_success()
        ctx.exit()

    def print_data(data):
        '''打印文件信息'''
        if isinstance(data, list):      # 打印列表
            utils.print_list(data,
                ['type\t', 'size\t', 'path\t\t', 'download_url'],
                ['\t', '\t', '\t\t', '']
            )
        elif isinstance(data, dict):    # 打印单个文件
            utils.print_dict(data, exclude=['_links'])
            pyperclip.copy(data['download_url'])
            logger.info('Now you can use download_url with {}.'.format(
                click.style('<CTRL-V>', fg='blue')
            ))

    def _del_file(path, sha):
        '''删除单个文件'''
        code, data = g.delete_file(owner, repo, path, sha)
        if code != 200:
            utils.print_failed()
            logger.error(path, filedata.get("message"))
            ctx.exit()
        logger.info(path, 'deleted')

    method = method.lower()
    if method == 'get':     # 处理 get 请求
        logger.info('Query file')
        logger.info('Owner\t: {}'.format(owner))
        logger.info('Repo\t: {}'.format(repo))
        logger.info('Path\t: {}'.format(path))
        logger.info('Waiting...')
        code, data = g.get_file(owner, repo, path)
        if code == 200:
            print_data(data)
            utils.print_success()
        else:
            utils.print_failed()
            logger.error(data.get("message"))
    elif method == 'delete':
        logger.info('Delete file')
        logger.info('Owner\t: {}'.format(owner))
        logger.info('Repo\t: {}'.format(repo))
        logger.info('Path\t: {}'.format(path))
        logger.info('Waiting...')
        code, filedata = g.get_file(owner, repo, path)
        if code != 200:
            utils.print_failed()
            logger.error(filedata.get("message"))
            ctx.exit()

        if isinstance(filedata, list):      # 删除文件夹

            if not yes:                     # 确认是否删除
                if not click.confirm('The {} is a folder, are you sure to delete?'.format(path)):
                    ctx.exit()
            else:
                logger.warn('The {} is a folder and is now being deleted'.format(path),
                        with_color=True)

            for f in filedata:
                _del_file(f['path'], f['sha'])

        elif isinstance(filedata, dict):    # 删除文件
            sha = filedata.get("sha")
            _del_file(path, sha)

        utils.print_success()


@run.command()
@click.option('--method', '-m', default = 'GET',
    help = 'GET/POST/PUT/DELETE for repository. Default is GET')
@click.option('--orga', '-o', help = 'If want create organization repository. Is required')
@click.argument('name', required = False)
@click.pass_context
def repo(ctx, name, orga, method):
    '''
    Get/Create your repositorys
    '''
    g = ctx.obj
    if not g:
        click.echo('You have not logged in yet, please run goss-cli to login')
        ctx.exit()

    owner = orga if orga else g.owner

    #  def print_repo_detail(r):
        #  '''打印单个 repository'''
        #  #  click.secho('*' * 60, fg='yellow')
        #  id_text = click.style('Id', fg='red')
        #  click.echo('{}     : {}'.format(utils.make_error_msg('Id'), r['id']))
        #  click.echo('{}   : {}'.format(utils.make_error_msg('Name'), r['name']))
        #  click.echo('{}  : {}'.format(utils.make_error_msg('Owner'),
            #  r['owner']['login']))
        #  click.echo('{}    : {}'.format(utils.make_error_msg('Url'),
            #  r['html_url']))
        #  click.echo('{}   : {}'.format(utils.make_error_msg('Desc'),
            #  r['description']))
        #  #  click.echo('{} : {}'.format('Detail', r['url']))
        #  click.echo('More details see: {}'.format(click.style(r['url'], fg='blue')))
        #  #  click.secho('*' * 60, fg='yellow')

    method = method.lower()
    if method == 'get':     # 处理 get 请求
        if name:            # 获取单个 repository
            logger.info('Query repository {}/{}'.format(owner, name))
            logger.info('Waiting...')
            code, repo = g.get_repository(owner, name)
            if code != 200:
                utils.print_failed()
                logger.error(repo.get("message"))
                ctx.exit()
            #  print_repo_detail(repo)
            utils.print_dict(repo, ['owner'])
            utils.print_success()
            ctx.exit()

        # 获取全部 repositorys
        logger.info('Query your repositorys.')
        logger.info('Waiting...')
        code, repos = g.get_owner_repositorys()
        if code != 200:
            utils.print_failed()
            logger.error(repo.get("message"))
            ctx.exit()
        utils.print_list(repos, 
            ['id\t\t', 'name\t', 'full_name\t', 'url'],
            ['\t', '\t', '\t', ''],
                )
        utils.print_success()
        ctx.exit()
    elif method == 'post':
        logger.info("Create repository")
        logger.info("Url : https://github.com/{}/{}".format(owner, name))
        logger.info('Waiting...')
        code, data = g.create_repository(name)
        if code != 201:
            utils.print_failed()
            logger.error(data.get("message"))
        logger.info("Create README.md")
        logger.info("Url : https://github.com/{}/{}/blob/master/README.md".format(owner, name))
        logger.info('Waiting...')
        code, data = g.create_file_from_url(owner, name,
            'https://raw.githubusercontent.com/wxnacy/goss/master/create_readme.md',
            'README.md')
        if code != 201:
            utils.print_failed()
            logger.error(data.get("message"))
        utils.print_success()


    elif method == 'delete':
        logger.info("Delete repository")
        logger.info("Url : https://github.com/{}/{}".format(owner, name))
        logger.info('Waiting...')
        code, data = g.delete_repository(owner, name)
        if code == 204:
            utils.print_success()
        else:
            utils.print_failed()
            logger.error(data.get("message"))


@run.command()
@click.argument('name', required = False)
@click.argument('value', required = False)
@click.pass_context
def config(ctx, name, value):
    '''
    Get/Create/Update goss config
    '''
    if name and value and '.' in name:
        names = name.split('.')
        section = names[0]
        key = names[1]
        utils.config(GOSS_CONFIG_PATH, section, **{key: value})
        utils.print_success()
        return

    conf = configparser.ConfigParser()
    conf.read(GOSS_CONFIG_PATH)
    secs = conf.sections()
    for sec in secs:
        click.echo('[{}]'.format(sec))
        kv = conf[sec]
        for k, v in kv.items():
            click.echo('    {} = {}'.format(k, v))

@run.command()
@click.option('--method', '-m', default = 'GET',
    help = 'GET/POST/PUT/DELETE for repository. Default is GET')
@click.option('--orga', '-o', help = 'If want create organization repository. Is required')
@click.option('--download', '-D', is_flag = True, help = 'Download file')
@click.option('--yes', '-y', is_flag = True, default = False, help = 'All questions answered yes')
@click.option('--output', '-O', help = 'Download name. Default is file name')
@click.option('--repo', '-r', help = 'Repository name. Default use config repo.name')
@click.argument('id', default="")
@click.pass_context
def release(ctx, repo, id, orga, method, download, output, yes):
    '''
    Get/Create/Delete/Download your Release/Asset

    More usage see : goss --help
    '''
    g = ctx.obj
    if not g:
        click.echo('You have not logged in yet, please run goss-cli to login')
        ctx.exit()

    r = g.get_release()
    owner = orga if orga else g.owner
    repo = repo if repo else goss_config.get_value('repo', 'name')

    def _get():
        if id:
            logger.info(f"Query release: {id}")
            logger.info(f"Owner:\t{owner}")
            logger.info(f"Repo:\t{repo}")
            logger.info("Waiting...")
            code, data = r.get_release(owner, repo, id)
            if code != 200:
                utils.print_failed()
                logger.error(repo.get("message"))
                ctx.exit()
            data.pop('author')
            utils.print_dict(data)
        else:
            logger.info("Query releases")
            logger.info(f"Owner:\t{owner}")
            logger.info(f"Repo:\t{repo}")
            logger.info("Waiting...")
            code, data = r.get_releases(owner, repo)
            if code != 200:
                utils.print_failed()
                logger.error(repo.get("message"))
                ctx.exit()
            utils.print_list(data,
                ['id\t\t', 'name\t', 'tag_name'],
                ['\t', '\t', ''],
            )
            logger.info('Now you can see the detail with command:')
            logger.info('\t\tgoss-cli release <id>')
        utils.print_success()
        ctx.exit()

    method_function = {
        'get': _get
    }
    method = method.lower()
    method_function[method]()



if __name__ == "__main__":
    run()
    #  credentials()
