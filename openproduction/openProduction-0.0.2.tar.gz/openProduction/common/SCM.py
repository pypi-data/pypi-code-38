import logging
import datetime
from datetime import timezone
from openProduction.common import misc, Version, Constants
from git import Repo
import collections
import os
import git
import shutil

def createHierarchy(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = createHierarchy(d.get(k, {}), v)
        else:
            if k not in d:
                d[k] = v
    return d

class SCM:
    
    def __init__(self, scmDir, config):
        self.config = config
        self.logger = logging.getLogger(misc.getAppName())
        self.username = config["git_username"]
        self.email = config["git_usermail"]
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.environ['GIT_ASKPASS'] = os.path.join(project_dir, 'askpass.py')
        os.environ['GIT_USERNAME'] = config["git_username"]
        os.environ['GIT_PASSWORD'] = config["git_password"]
        
        if os.path.exists(scmDir) == False:
            self.logger.info("repo directory %s doesn't exist, cloning again"%scmDir)
            os.makedirs(scmDir)
            Repo.clone_from(config["git_url"], scmDir)
        
        self.scmDir = scmDir
        self.repo = Repo.init(scmDir)
        self.repo.config_writer().set_value("user", "name", self.username).release()
        self.repo.config_writer().set_value("user", "email", self.email).release()
        
        if len(self.repo.remotes) == 0:
            self.logger.info("repo has no remote information, adding url %s"%config["git_url"])
            self.repo.create_remote('origin', config["git_url"])
        
        self.logger.info("fetching changes from remote")
        self.repo.remotes.origin.fetch()
        
        self.createGitignore(self.scmDir)
        self.repo.git.add(".gitignore")
        
    def getURL(self):
        return self.repo.remotes.origin.url
        
    def createGitignore(self, folder):
        ignore = ["__pycache__/", "*.py[cod]", "*$py.class"]
        
        fname = os.path.join(folder, ".gitignore")
        if os.path.exists(fname) == False:
            f = open(fname, "w")
            f.write('\n'.join(ignore) + '\n')
            f.close()
        else:
            wlines = []
            #check if exists
            f = open(fname, "r+")
            lines = f.read().splitlines()
            for i in ignore:
                if i not in lines:
                    wlines.append(i)
            for w in wlines:
                f.write(w+"\n")
            f.close()
        
    def isDirty(self):
        return self.repo.is_dirty()
    
    def scmDirHasChanges(self):
        diff = self.repo.git.diff(self.scmDir)
        if diff == '':
            changed = False
        else:
            changed = True
        return changed
            
    def checkoutProductRevision(self):
        if self.getURL() != self.config["git_url"]:
            self.logger.info("remote url in local working copy doesn't match. Wipe out working copy")
            shutil.rmtree(self.scmDir)
            os.makedirs(scmDir)
            Repo.clone_from(self.config["git_url"], scmDir)
            self.repo = Repo.init(scmDir)
            
        self.repo.git.checkout(self.config["commit_id"])
        
    def getBaseDir(self):
        return self.scmDir
    
    def addFile(self, file):
        self.repo.index.add([file])
