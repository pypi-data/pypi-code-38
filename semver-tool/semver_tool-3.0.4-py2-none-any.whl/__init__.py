from .__version__ import version as __version__

import subprocess as sp
import datetime
import logging
import re
import os
from dateutil.parser import parse as dateparse

log = logging.getLogger("gwsa")


class SemVer(object):
    def __init__(self, vmajor, vminor, vpatch, pre_release, build):
        self.info = {
            "major": int(vmajor),
            "minor": int(vminor),
            "patch": int(vpatch),
            "pre_release": self.fix_token_array(pre_release),
            "build": self.fix_token_array(build)
        }

    def fmt(self, fmt='MNPRB'):
        mnp = []
        if 'M' in fmt:
            mnp.append(str(self.info['major']))
        if 'N' in fmt:
            mnp.append(str(self.info['minor']))
        if 'P' in fmt:
            mnp.append(str(self.info['patch']))
        ver = '.'.join(mnp)
        if 'R' in fmt:
            if self.info['pre_release']:
                ver += '-' + self.info['pre_release']
        if 'B' in fmt:
            if self.info['build']:
                ver += '+' + self.info['build']
        return ver

    def __str__(self):
        return self.fmt()

    def __repr__(self):
        return self.fmt()

    def fix_token_array(self, arr):
        def fix_token(tok):
            rc = [ (c if (c == '-' or c.isalnum()) else '.') for c in tok]
            return ''.join(rc)

        rc = [ fix_token(t) for t in arr ]
        return '.'.join(rc)

def run(cmd):
    return sp.check_output(cmd, shell=True).strip()

class GitSemVer(object):
    def __init__(self, root, fmt):
        self.info = self.get_git_info(root)
        self.fmt = fmt
        self.sm = self.get_sm()

    def get_git_info(self, root):
        info = {}
        os.chdir(root)
        info['branch'] = run('git rev-parse --abbrev-ref HEAD')
        log.debug("branch is %s",  info['branch'])
        if info['branch'] == 'HEAD':
            # log.debug("branch is HEAD %s",  info['branch'])
            var = 'CI_COMMIT_REF_NAME'
            if var in os.environ:
                info['branch'] = os.environ[var]
        tmp = run('git describe --long --dirty')
        # format: 2.0.0-0-g20f425b-dirty
        log.debug("commit desc %s", tmp)
        tmp = tmp.split('-')
        if tmp[-1] == 'dirty':
            info['dirty'] = True
            info['date'] = datetime.datetime.now()
            del tmp[-1]
        else:
            info['dirty'] = False
            info['date'] = dateparse(run('git log -1 --format=%ci'))
        info['hash'] = tmp[-1][1:]
        del tmp[-1]
        info['count'] = int(tmp[-1])
        del tmp[-1]
        info['tag'] = '-'.join(tmp)
        # log.debug("info %s", info)

        re_mnp = 'v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
        m = re.match(re_mnp, info['tag'])
        if not m:
            log.error("%s is not SemVer tag, eg [v]M.N.P", ver[0])
            exit(1)

        info.update(m.groupdict())
        log.debug("info %s", info)

        return info

    def is_release_branch(self):
        b = self.info['branch']
        if b == 'master':
            return True
        if b.startswith('release/'):
            return True
        return False

    def get_sm(self):
        major = self.info['major']
        minor = self.info['minor']
        patch = self.info['patch']
        rel = []
        build = []
        if self.info['count'] == 0 and self.info['dirty'] == False:
            return SemVer(major, minor, patch, rel, build)
        patch = int(patch) + 1
        if not self.is_release_branch():
            rel.append(self.info['branch'])
        if self.info['dirty']:
            self.info['count'] += 1
        if self.info['count']:
            rel += ['rc', str(self.info['count'])]
        build += ['git', self.info['hash']]
        build += ['time', self.info['date'].strftime("%Y%m%dT%H%M")]

        return SemVer(major, minor, patch, rel, build)

    def __str__(self):
        return self.sm.fmt(self.fmt)
