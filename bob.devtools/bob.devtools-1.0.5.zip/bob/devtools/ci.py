#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Tools to help CI-based builds and artifact deployment'''


import git
import distutils.version

from .log import get_logger
logger = get_logger(__name__)


def is_master(refname, tag, repodir):
  '''Tells if we're on the master branch via ref_name or tag

  This function checks if the name of the branch being built is "master".  If a
  tag is set, then it checks if the tag is on the master branch.  If so, then
  also returns ``True``, otherwise, ``False``.

  Args:

    refname: The value of the environment variable ``CI_COMMIT_REF_NAME``
    tag: The value of the environment variable ``CI_COMMIT_TAG`` - (may be
      ``None``)

  Returns: a boolean, indicating we're building the master branch **or** that
  the tag being built was issued on the master branch.
  '''

  if tag is not None:
    repo = git.Repo(repodir)
    _tag = repo.tag('refs/tags/%s' % tag)
    return _tag.commit in repo.iter_commits(rev='master')

  return refname == 'master'


def is_stable(package, refname, tag, repodir):
  '''Determines if the package being published is stable

  This is done by checking if a tag was set for the package.  If that is the
  case, we still cross-check the tag is on the "master" branch.  If everything
  checks out, we return ``True``.  Else, ``False``.

  Args:

    package: Package name in the format "group/name"
    refname: The current value of the environment ``CI_COMMIT_REF_NAME``
    tag: The current value of the enviroment ``CI_COMMIT_TAG`` (may be
      ``None``)
    repodir: The directory that contains the clone of the git repository

  Returns: a boolean, indicating if the current build is for a stable release
  '''

  if tag is not None:
    logger.info('Project %s tag is "%s"', package, tag)
    parsed_tag = distutils.version.LooseVersion(tag[1:]).version  #remove 'v'
    is_prerelease = any([isinstance(k, str) for k in parsed_tag])

    if is_prerelease:
      logger.warn('Pre-release detected - not publishing to stable channels')
      return False

    if is_master(refname, tag, repodir):
      return True
    else:
      logger.warn('Tag %s in non-master branch will be ignored', tag)
      return False

  logger.info('No tag information available at build')
  logger.info('Considering this to be a pre-release build')
  return False


def comment_cleanup(lines):
  """Cleans-up comments and empty lines from textual data read from files"""

  no_comments = [k.partition('#')[0].strip() for k in lines]
  return [k for k in no_comments if k]


def read_packages(filename):
  """
  Return a python list of tuples (repository, branch), given a file containing
  one package (and branch) per line.  Comments are excluded

  """
  # loads dirnames from order file (accepts # comments and empty lines)
  with open(filename, 'rt') as f:
    lines = comment_cleanup(f.readlines())

  packages = []
  for line in lines:
    if ',' in line:  #user specified a branch
      path, branch = [k.strip() for k in line.split(',', 1)]
      packages.append((path, branch))
    else:
      packages.append((line, 'master'))

  return packages


def uniq(seq, idfun=None):
  """Very fast, order preserving uniq function"""

  # order preserving
  if idfun is None:
      def idfun(x): return x
  seen = {}
  result = []
  for item in seq:
      marker = idfun(item)
      # in old Python versions:
      # if seen.has_key(marker)
      # but in new ones:
      if marker in seen: continue
      seen[marker] = 1
      result.append(item)
  return result
