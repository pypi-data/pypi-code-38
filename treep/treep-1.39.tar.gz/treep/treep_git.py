# Treep, copyright 2019 Max Planck Gesellschaft
# Author : Vincent Berenz 

# This file is part of Treep.

#    Treep is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Treep is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Treep.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import print_function

import git,sys,os,time,multiprocessing

from .status import Status

from .process_calls import execute


def clone(url,destination_path,submodules=True):
    git.Repo.clone_from(url,destination_path)


def clone_submodules(path):
    os.chdir(path)
    nb_cpus = multiprocessing.cpu_count()
    nb_cpus -= 1
    if nb_cpus <= 0 :
        nb_cpus=1
    execute("git submodule update --init --recursive")
    
def current_branch(path):
    repo = git.Repo.init(path)
    return str(repo.active_branch)


def list_branches(path):

    def _extract_branch_name(line):
        line = line.replace('\\n','')
        line = line.replace("'","")
        if "->" in line:
            return _extract_branch_name(line[line.rfind("->") + 2:])
        try:
            line = line[line.rfind("/") + 1:]
        except BaseException:
            pass
        line = line.replace("*", "")
        line = line.strip()
        return str(line)

    os.chdir(path)
    out = execute("git branch -a")
    lines = out.split("\n")
    branches = [_extract_branch_name(line) for line in lines]
    return branches
    

def status_message(path):
    os.chdir(path)
    message = execute("git status")
    return str(message)

def create_branch(path,branch_name):
    os.chdir(path)
    try :
        execute("git checkout -b "+str(branch_name))
    except :
        raise Exception("failed to create branch "+branch_name)
        
def checkout_branch(path,branch_name,create=False):
    branches = list_branches(path)
    if branch_name in branches:
        repo = git.Repo.init(path)
        repo.git.checkout(branch_name)
        return
    else :
        if not create:
            raise Exception("no such branch")
        else :
            create_branch(path,branch_name)

def list_tags(path):
    os.chdir(path)
    tags = execute("git tag")
    return tags
            
def checkout_tag(path,tag):
    tags = list_branches(path)
    if tag in tags:
        repo = git.Repo.init(path)
        repo.git.checkout(tag)
        return
    else :
        raise Exception("no such tag")

def checkout_commit(path,commit):
    repo = git.Repo.init(path)
    try:
        repo.git.checkout(commit)
    except Exception as e:
        raise Exception("failed to checkout commit "+str(commit)+": "+str(e))
    

def push_to_origin(path,branch):
    # note: not using gitpython: could not understand
    #       how to get the info if the push was a success or not,
    #       experienced pushed that returned undocumented status
    #       messages
    # below throws an exception in case of failure
    os.chdir(path)
    execute("git push origin "+branch)

    
def fetch_origin(path):
    repo = git.Repo.init(path)
    origin = repo.remotes.origin
    origin.fetch()


def add_all(path):
    os.chdir(path)
    execute("git add -A .")
    repo = git.Repo.init(path)
    nb_staged_files = len(repo.index.diff("HEAD"))
    return nb_staged_files


def _get_origin(path,pattern):
    os.chdir(path)
    out = execute("git remote show origin")
    lines = out.split("\n")
    for line in lines:
        if pattern in line and "URL:" in line:
            return line[line.index("URL:")+4:]
    

def get_fetch_origin(path):
    return _get_origin(path,"Fetch")


def get_push_origin(path):
    return _get_origin(path,"Push")


def set_origin(path,origin):
    os.chdir(path)
    out = execute("git remote set-url origin "+origin)

def commit(path,message):
    repo = git.Repo.init(path)
    repo.index.commit(str(message))


def pull(path):
    os.chdir(path)
    out = execute("git pull")
    return out

def local_modifications(path):
    git_status = status_message(path)
    repo = git.Repo(path=path)
    if repo.untracked_files:
        return True
    if ("up-to-date" not in git_status) or ("clean" not in git_status):
        return True
    return False

    
def get_status(path):

    try :
        repo = git.Repo(path=path)
    except :
        return None

    status = Status()

    status.repo_name = os.path.basename(path)
    status.path = path

    try:
        branch = str(repo.active_branch)
    except Exception as e:
        if "detached" in str(e):
            branch = ("(detached head)")
        else :
            raise e
    status.branch = branch

    # information about last commit on current branch
    
    try :
        commit_instance = repo.commit()
    except ValueError:
        # this happens for example for a repo with no commits
        commit_instance = None

    if commit_instance is not None:
        status.commit_sha1 = repo.head.object.hexsha 
        status.commit_author = commit_instance.author
        status.commit_message = commit_instance.message
        status.commit_summary = commit_instance.summary
        status.commit_date = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(commit_instance.authored_date))
        
    # information about remote 'origin'
        
    status.origin = repo.remote(name='origin').url

    # diff with master origin

    if local_modifications(path):
        status.local_modifications = True
        try:
                                       # local modif                # staged files
            status.nb_modified_files = len(repo.index.diff(None)) + len(repo.index.diff("HEAD")) 
        except :
            # happens on empty repositories
            status.nb_modified_files = 0
    else :
        status.local_modifications = False

    git_status = status_message(path)
        
    if status.local_modifications:
        status.status_message = git_status
    else :
        status.status_message = None
        
    if "behind" in git_status:
        status.behind_origin = True
    else :
        status.behind_origin = False

    if "ahead" in git_status:
        status.ahead_origin = True
    else :
        status.ahead_origin = False
    
    return status
    
    
