# -*- coding: utf-8 -*-
# vim: set et sts=2:
# pylint: disable-msg=W0311,C0301,C0103,C0111


import os
import re
import shutil

from git import Repo
from flask import jsonify


def cloneRepo(url, workDir, user="", email=""):
  """Clone a repository
  Args:
    workDir is the path of the new project
    url is the url of the repository to be cloned
    email is the user's email
    user is the name of the user"""

  if not workDir:
    return jsonify(code=0,
                   result="Can not create project folder.")

  if os.path.exists(workDir) and len(os.listdir(workDir)) < 2:
    shutil.rmtree(workDir)  # delete useless files
  repo = Repo.clone_from(url, workDir)
  config_writer = repo.config_writer()
  config_writer.add_section("user")
  if user != "":
    config_writer.set_value("user", "name", user.encode("utf-8"))
  if email != "":
    config_writer.set_value("user", "email", email)

def updateGitConfig(repository, user, email):
  if not os.path.exists(repository):
    return
  repo = Repo(repository)
  config_writer = repo.config_writer()
  if user != "":
    config_writer.set_value("user", "name", user)
  if email != "":
    config_writer.set_value("user", "email", email)
  config_writer.release()

def gitStatus(project):
  """Run git status and return status of specified project folder
  Args:
    project: path of the projet to get status
  Returns:
    a list with (result of git status, current branch, isdirty)"""

  repo = Repo(project)
  git = repo.git
  result = git.status().replace('#', '')
  branch = git.branch().replace(' ', '').split('\n')
  isdirty = repo.is_dirty(untracked_files=True)
  return (result, branch, isdirty)


def switchBranch(project, branch):
  """Switch a git branch
  Args:
    project: directory of the local git repository
    name: switch from current branch to `name` branch"""

  repo = Repo(project)
  current_branch = repo.active_branch.name
  if branch == current_branch:
    return False
  else:
    git = repo.git
    git.checkout(branch)
    return True


def addBranch(project, name, onlyCheckout=False):
  """Add new git branch to the repository
  Args:
    project: directory of the local git repository
    name: name of the new branch
    onlyCheckout: if True then the branch `name` is created before checkout
  Returns:
    True or False"""
  
  if not os.path.exists(project):
    return False
  repo = Repo(project)
  git = repo.git
  if not onlyCheckout:
    git.checkout('-b', name)
  else:
    git.checkout(name)
  return True


def getDiff(project):
  """Get git diff for the specified project directory"""
  result = ""
  try:
    repo = Repo(project)
    git = repo.git
    current_branch = repo.active_branch.name
    result = git.diff(current_branch)
  except Exception as e:
    result = safeResult(str(e))
  return result

def gitCommit(project, msg):
  """Commit changes for the specified repository
  Args:
    project: directory of the local repository
    msg: commit message"""
  code = 0
  json = ""
  repo = Repo(project)
  if repo.is_dirty:
    git = repo.git
    #add file to be commited
    files = repo.untracked_files
    for f in files:
      git.add(f)
    #Commit all modified and untracked files
    git.commit('-a', '-m', msg)
    code = 1
  else:
    json = "Nothing to be commited"
  return jsonify(code=code, result=json)

def gitPush(project):
  """Push changes for the specified repository
  Args:
    project: directory of the local repository
    msg: commit message"""
  code = 0
  json = ""
  try:
    repo = Repo(project)
    git = repo.git
    #push changes to repo
    current_branch = repo.active_branch.name
    git.push('origin', current_branch)
    code = 1
  except Exception as e:
    json = safeResult(str(e))
  return jsonify(code=code, result=json)


def gitPull(project):
  result = ""
  code = 0
  try:
    repo = Repo(project)
    git = repo.git
    git.pull()
    code = 1
  except Exception as e:
    result = safeResult(str(e))
  return jsonify(code=code, result=result)


def safeResult(result):
  """Parse string and remove credential of the user"""
  regex = re.compile("(https:\/\/)([\w\d\._-]+:[\w\d\._-]+)\@([\S]+\s)", re.VERBOSE)
  return regex.sub(r'\1\3', result)
