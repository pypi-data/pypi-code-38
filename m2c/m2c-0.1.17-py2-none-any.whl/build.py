#!/usr/bin/env python
#coding: utf-8
#by yangbin at 2018.11.28

import os
import sys
import json
import time

from .conf import *
from .m2c import goswagger

# amd64 only
os.environ.update({
    "CGO_ENABLED": "0",
    "GOARCH": "amd64"
})

# auto gen build details
date = time.strftime('%Y%m%d', time.localtime())
head = os.popen('git rev-parse HEAD').read()
ldflags = " ".join([
    '-extldflags -static',
    '-X main.BuildDate=%s' %  date,
    '-X main.BuildGitHash=%s' % head
])

def _get_version():
    for line in open(os.path.join(GOPHER_DIR, 'main.go')):
        line = line.strip()
        if not line.startswith('version'):
            continue

        items = map(lambda x:x.strip(), line.split('='))
        if len(items) != 2 or items[0] != 'version':
            continue

        return items[1].strip('"')


def _get_name():
    return json.loads(open(M2C_PATH).read())['name']


def _get_logdir():
    name = _get_name()
    return os.path.join(LOG_HOME, name)


def _run(cmd):
    print 'running: %s' % cmd
    code = os.system(cmd)
    if code != 0:
        print Color.red('run: %s failed' % cmd)
    else:
        print Color.green('run: %s success' % cmd)


def version():
    print _get_version()


def name():
    print _get_name()


def build():
    os.chdir(GOPHER_DIR)
    app = os.path.join(BUILD_DIST, _get_name())
    cmds = [
        'mkdir -p %s' % BUILD_DIST,
        'go mod vendor',
        'go build -mod=vendor -ldflags "%s" -o %s .' % (ldflags, app),
    ]
    map(_run, cmds)
    print 'Done'


def build_linux():
    os.environ.update({
        "GOOS": "linux",
    })
    os.chdir(GOPHER_DIR)
    app = os.path.join(BUILD_DIST, _get_name())
    cmds = [
        'mkdir -p %s' % BUILD_DIST,
        'go mod vendor',
        'go build -mod=vendor -ldflags "%s" -o %s .' % (ldflags, app),
    ]
    map(_run, cmds)
    print 'Done'


def pack(env='dev'):
    build()
    name = _get_name()
    version = _get_version()
    dist = os.path.join(BUILD_DIST, '%s-%s.tar.gz' % (name, version))
    cfg = os.path.join(GOPHER_DIR, 'config', '%s.yaml' % env)
    os.system('cp %s %s' % (cfg, BUILD_DIST))
    files = " ".join([name, '%s.yaml' % env])

    os.chdir(BUILD_DIST)
    cmds = [
        'tar -zcf %s %s' % (dist, files)
    ]
    map(_run, cmds)

    print 'name: %s' % name
    print 'version: %s' % version
    print 'pack: %s' %  dist

    
def packall():
    build()
    goswagger()

    name = _get_name()
    version = _get_version()
    app = os.path.join('dist', name)
    dist = os.path.join('dist', '%s-%s-all.tar.gz' % (name, version))
    files = " ".join([app, 'docs', 'config.example.yaml'])

    cmds = [
        'tar -zcf %s %s' % (dist, files)
    ]
    map(_run, cmds)

    print 'name: %s' % name
    print 'version: %s' % version
    print 'pack: %s' %  dist


def packsrc():
    name = _get_name()
    version = _get_version()
    dist = os.path.join('dist', '%s-%s-src.tar.gz' % (name, version))

    cmds = [
        'tar -zcf %s %s' % (dist, 'gopher')
    ]
    map(_run, cmds)

    print 'name: %s' % name
    print 'version: %s' % version
    print 'pack: %s' %  dist


def clean():
    os.system('rm -rf dist/*')


def apidoc():
    config = {
        "name": "myapp",
        "version": "0.0.1",
        "description": "myapp api doc",
        "title": "myapp api doc",
        "url": "https://myapp.com/api"
    }

    cfg = os.path.join(GOPHER_DIR, 'config/dev.yaml')

    if os.path.exists(cfg):
        try:
            from yaml import load, Loader
            app = load(open(cfg), Loader)
            config['name'] = app['name']
            config['description'] = app['apiDoc']['desc']
            config['title'] = app['apiDoc']['title']
            config['url'] = app['apiDoc']['url']
        except:
            pass

    cmds = [
        'mkdir -p %s' % APIDOC_DIR
    ]
    map(_run, cmds)

    # doc.go
    goapidoc()

    open(os.path.join(APIDOC_DIR, 'apidoc.json'), 'wb').write(json.dumps(config, indent=2))
    cmds = [
        'cd %s && apidoc' % APIDOC_DIR
    ]

    map(_run, cmds)
    print 'Done'


def unittest():
    os.chdir(GOPHER_DIR)
    cmds = [
        'cd test/ && docker-compose run --rm unittest'
    ]
    map(_run, cmds)
    print 'Done'
    

def supervisor_conf(apphome='/data/app', env='dev'):
    conf = '''
[program:{APPNAME}]
directory={APPHOME}
command={APPBIN_PATH} -c {APPCONF_PATH}
autostart=true
autorestart=true
stdout_logfile={STDOUT_LOG_PATH}
stdout_logfile_maxbytes=50M
stderr_logfile={STDERR_LOG_PATH}
stderr_logfile_maxbytes=50M'''
    appname = _get_name()
    apphome = os.path.join(apphome, appname)
    appbin_path = os.path.join(apphome, appname)
    appconf_path = os.path.join(apphome, '%s.yaml' % env)
    logdir = _get_logdir()
    if not os.path.isabs(logdir):
        if logdir.startswith('./'):
            logdir = logdir.lstrip('./')
        logdir = os.path.join(apphome, logdir)
    stdout_log_path = os.path.join(logdir, '%s_stdout.log' % appname)
    stderr_log_path = os.path.join(logdir, '%s_stderr.log' % appname)
    print conf.format(**{
        "APPNAME": appname, 
        "APPHOME": apphome, 
        "APPBIN_PATH": appbin_path, 
        "APPCONF_PATH": appconf_path,
        "STDOUT_LOG_PATH": stdout_log_path,
        "STDERR_LOG_PATH": stderr_log_path,
    })


def run(*args):
    goswagger()
    from watchgo import WatchGo
    os.chdir(GOPHER_DIR)
    command = ['go', 'run', '.']
    if args:
        command.extend(args)
    WatchGo(command, GOPHER_DIR).start_watch()

def debug():
    os.chdir(GOPHER_DIR)
    os.system('dlv debug .')
