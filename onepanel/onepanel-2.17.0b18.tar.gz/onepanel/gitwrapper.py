""" Command line interface for the OnePanel Machine Learning platform

Wrap git commands and provide transparent integration onepanel commands with the git.
"""

import glob
import os
import subprocess
import onepanel


class GitWrapper:
    def __init__(self):
        self.HOST = os.getenv('GITLAB_GIT_HOST', 'git.onepanel.io')

    def init(self,onepanel_user_uid,gitlab_token,home, account_uid, project_uid):
        git_cmd = 'git init'
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()

        git_cmd = 'git remote add onepanel https://{}:{}@{}/{}/{}.git'.format(
            onepanel_user_uid,
            gitlab_token,
            self.HOST,
            account_uid,
            project_uid
        )
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()

    def clone(self,onepanel_user_uid,gitlab_token, home, account_uid, project_uid, ext=''):
        git_cmd = 'git clone -o onepanel https://{}:{}@{}/{}/{}{}.git {}'.format(
            onepanel_user_uid,
            gitlab_token,
            self.HOST,
            account_uid,
            project_uid,
            ext,
            home
        )
        p = subprocess.Popen(git_cmd, shell=True)
        p.wait()

        return p.returncode

    def exclude(self, home, files):
        exclude_file = os.path.join(home, '.git/info/exclude')
        with open(exclude_file,'a+') as f:
            for file in files:
                f.write(file + '\n')