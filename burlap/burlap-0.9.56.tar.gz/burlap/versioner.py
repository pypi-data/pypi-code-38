#!/usr/bin/python
"""
File: versioner.py

A utility for detecting the release of software library updates
from numerous sources.

Copyright (C) 2012  Chris Spencer (chrisspen at gmail dot com)

Helps you query and track software package versions.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""
from __future__ import unicode_literals, print_function

import subprocess
import csv
import os
import re
import sys
import json

from six.moves import xmlrpc_client as xmlrpclib
from six.moves.urllib.request import urlopen

try:
    import feedparser
except ImportError:
    print('Warning: feedparser not installed', file=sys.stderr)
    feedparser = None

PIP = 'pip'
GITHUB = 'github' # Most recent commit.
GITHUB_TAG = 'github_tag' # Most recent tag.
RSS = 'rss'
APT = 'apt'
TYPES = (
    PIP,
    GITHUB,
    GITHUB_TAG,
    RSS,
    APT,
)

GITHUB_PATTERN = re.compile(
    r'https://github.com/(?P<user>[^/]+)/(?P<repo>[^/$]+)')

DEP_SCHEMA = (
    'type',
    'name',
    'uri',
    'version',
    'rss_field',
    'rss_regex',
)

def get_github_user_repo(uri):
    matches = GITHUB_PATTERN.findall(uri)
    if not matches:
        return
    user, repo = matches[0]
    return user, repo

VERSIONER_FN = os.getenv('BURLAP_VERSIONER_FN', '~/.burlap_versioner_pip')

def get_pip_oath():
    assert os.path.isfile(VERSIONER_FN), 'Credentials file %s does not exist.' % VERSIONER_FN
    client_id, client_secret = open(VERSIONER_FN, 'r').read().strip().split(',')
    return client_id, client_secret

class Dependency:

    def __init__(self, type, name, uri, version, rss_field, rss_regex): # pylint: disable=redefined-builtin
        self.type = type # source location, e.g. pip|github|rss|apt|etc
        assert type in TYPES, 'Unknown type: %s' % (self.type,)
        self.name = name
        self.uri = uri
        self.version = version
        self.rss_field = rss_field
        self.rss_regex = rss_regex
        self._cache = {}

    def __str__(self):
        return u'%s==%s' % (self.name, self.version)

    def _get_current_version_pip(self):
        client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
        v = client.package_releases(self.uri)
        if v:
            return v[0]

    def _get_current_version_github(self):
        #TODO:use authentication to avoid rate-limiting?
        user, repo = get_github_user_repo(self.uri)
        url = 'https://api.github.com/repos/%s/%s/git/refs/heads/master' \
            % (user, repo,)
        resp = urlopen(url).read()
        resp = json.loads(resp)
        return resp['object']['sha']

    def _get_current_version_github_tag(self):
        # check rate limiting with:
        # curl -i https://api.github.com/users/whatever
        # Note, while unauthenticated, we can only access this url 60-times an hour.
        #TODO:use authentication to avoid rate-limiting?
        user, repo = get_github_user_repo(self.uri)
        url = 'https://api.github.com/repos/%s/%s/tags' % (user, repo,)
        #print 'url:',url
        resp = urlopen(url).read()
        resp = json.loads(resp)
        resp = sorted(
            resp,
            key=lambda o: tuple(int(_) if _.isdigit() else _ \
                for _ in o['name'].split('.')),
            reverse=True)
        for tag in resp:
            v = tag['name']
            if self.name in v:
                v = v.replace(self.name, '')
            if not v[0].isalnum():
                v = v[1:]
            return v

    def _get_current_version_apt(self):
#        cmd = ("apt-get upgrade --dry-run %(uri)s | grep \"Conf %(uri)s\" " + \
#            "| awk '{gsub(/[()]/,\"\"); print($3;}'") % dict(uri=self.uri)
        cmd = ("dpkg -s %(uri)s | grep -E \"Version:\" " + \
            "| awk '{gsub(/[()]/,\"\"); print($2;}'") % dict(uri=self.uri)
        #print cmd
        out = subprocess.check_output(cmd, shell=True)
        #print out
        return out

    def _get_current_version_rss(self):
        resp = feedparser.parse(self.uri)
        pat = re.compile(self.rss_regex)
        for entry in resp.entries:
            matches = pat.findall(getattr(entry, self.rss_field))
            if matches:
                return matches[0]

    def get_current_version(self):
        if '_current_version' not in self._cache:
            self._cache['_current_version'] = \
                getattr(self, '_get_current_version_%s' % self.type)()
        return self._cache['_current_version']

    def is_stale(self):
        cv = self.get_current_version()
        if not cv:
            return
        return cv != self.version

    def is_fresh(self):
        return not self.is_stale()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Track library dependency versions.')
    parser.add_argument('--file', dest='file', default=None,
        help='The CSV dependency file.')
    parser.add_argument('--stale', dest='stale', action='store_true',
        default=False,
        help='Only lists dependencies that have a more recent version.')
    parser.add_argument('--line', dest='line',
        help='A comma-delimited line describing a dependency.')
    parser.add_argument('--pipout', dest='pipout', action='store_true',
        default=False,
        help='If set, outputs a pip requirements file.')
    parser.add_argument('--pipin', dest='pipin',
        default=None,
        help='The filename of a pip requirements file to read and convert ' +
            'to a dependency file.')
    args = parser.parse_args()

    done = False
    if args.line:
        done = True
        dep = Dependency(*args.line.split(','))
        if dep.name == dep.uri:
            print(dep.name)
        else:
            print(dep.name, dep.uri)
        print('\tcurrent version:', dep.get_current_version())
        print('\tyour version:', dep.version)
        print('\tfresh:', dep.is_fresh())

    if args.file:
        done = True
        fn = args.file
        if not os.path.isfile(fn):
            print('Error: Dependency file %s does not exist.\n' % (fn,))
            parser.print_help()
            sys.exit(1)
        total_stale = 0
        total = 0
        for line in csv.DictReader(open(fn), delimiter=','):
            dep = Dependency(**dict((k, v) for k, v in line.items() if k))
            total += 1
            is_stale = dep.is_stale()
            total_stale += is_stale if is_stale is not None else 0
            if not args.stale or (args.stale and is_stale):
                if args.pipout:
                    if dep.type == PIP:
                        print('%s==%s' % (dep.uri, dep.version))
                    continue
                if dep.name == dep.uri:
                    print(dep.name)
                else:
                    print(dep.name, dep.uri)
                print('\tcurrent version:', dep.get_current_version())
                print('\tyour version:', dep.version)
                print('\tfresh:', dep.is_fresh())
        print('='*80)
        print('%i total dependencies' % total)
        print('%i total stale dependencies' % total_stale)
        print('%.0f%% fresh' % ((total-total_stale)/float(total)*100))

    if args.pipin:
        done = True
        fn = args.pipin
        if not os.path.isfile(fn):
            print('Error: PIP requirements file %s does not exist.\n' % (fn,))
            parser.print_help()
            sys.exit(1)
        print(','.join(DEP_SCHEMA))
        for line in open(fn, 'r').readlines():
            parts = line.strip().split('==')
            if not parts:
                continue
            args = dict(
                type='pip',
                name=parts[0],
                uri=parts[0],
                version=parts[1] if len(parts) >= 2 else '',
                rss_field='',
                rss_regex='')
            fmt = '%(type)s,%(name)s,%(uri)s,%(version)s,%(rss_field)s,' + \
                '%(rss_regex)s'
            print(fmt % args)

    if not done:
        parser.print_help()
        sys.exit(1)
