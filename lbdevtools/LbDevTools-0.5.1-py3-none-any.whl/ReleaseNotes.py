#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Generate release notes draft.

See `lb-gen-release-notes --help` for details.

"""


import re
import os
import sys
import argparse
import itertools
import logging
import datetime
import gitlab
from jinja2 import Environment, FileSystemLoader

import subprocess

from LbDevTools import __version__


def getOutput(*args, **kwargs):
    '''
    Helper function to get the standard output of a command.

    If the command fails, raise CalledProcessError (see subprocess.check_call).
    '''
    logging.debug('getting output of %s', subprocess.list2cmdline(args[0]))
    kwargs['stdout'] = subprocess.PIPE
    do_strip = not kwargs.pop('no_strip', False)
    proc = subprocess.Popen(*args, **kwargs)
    out, _ = proc.communicate()
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, args[0])
    if do_strip:
        out = out.strip()
    # logging.debug('\n==============\n%s==============', out)
    return out


def git(*args, **kwargs):
    '''
    Helper function to call git.
    '''
    args[0].insert(0, 'git')
    logging.debug('calling %s', args[0])
    subprocess.check_call(*args, **kwargs)


def git_o(*args, **kwargs):
    '''
    Helper function to get the output of a call to git.
    '''
    args[0].insert(0, 'git')
    return getOutput(*args, **kwargs)

def ref_names(repo, commit):
    '''
    Return matching ref names for a given commit.
    '''
    result = git_o(['log', '-1', '--decorate=full',
                    '--pretty=%d', commit], cwd=repo)
    return [x.strip() for x in result[1:-1].split(',')]


def find_merge_request_id(repo, merge_commit, second_parent):
    '''
    Find a merge request iid given a merge commit and its second parent.

    First tries to match the second parent to a merge request ref name.
    If this fails (e.g. for squashed commits), a match is attempted
    based on the merge commit message.
    '''
    names = ref_names(repo, second_parent)
    m = [re.match(r'^refs/remotes/origin/merge-requests/(\d+)$', name)
         for name in names]
    m = [_f for _f in m if _f]
    if m:
        if len(m) > 1:
            logging.warning(
                'Multiple merge requests associated with {}: {}. '
                'Taking the first.'
                .format(second_parent, [i.group(1) for i in m]))
        return int(m[0].group(1))
    logging.debug(
        'Second parent of {} ({}) does not correspond to a merge '
        'request ref.'.format(merge_commit, second_parent))
    # For squashed commits, the MR reference stays at the last MR commit
    # while the second parent is the new squashed commit. It is hard to
    # precisely match the commits, so let's look at the merge commit message
    message = git_o(['show', '-s', '--format=%B', merge_commit], cwd=repo)
    m = re.search('^See merge request [^ ]*!([0-9]+)$', message, re.MULTILINE)
    if m:
        return int(m.group(1))
    logging.warning(
        'Could not find MR for {} based on second parent ({}) refs or commit '
        'message.\nDid you squash _and_ modify message or did you even push '
        'directly from the command line?'.format(merge_commit, second_parent))
    return None


def find_merge_requests_git(project, repo, since, until=''):
    '''
    Find GitLab merge requests using the git commit history.
    '''
    git(['fetch', 'origin',
         '+refs/merge-requests/*/head:refs/remotes/origin/merge-requests/*'],
         cwd=repo)
    log = git_o(['log', '--first-parent', '--parents',
                 '--merges', '--pretty=oneline', '--no-color',
                 '{}..{}'.format(since, until)], cwd=repo)
    commits = [line.split()[:3] for line in log.splitlines()]
    iids = [find_merge_request_id(repo, commit[0], commit[2])
            for commit in commits]
    iids = [iid for iid in iids if iid]
    # .list(iids=iids) produces a wrong query, so do it semi-manually:
    # TODO fix this in a future version of python-gitlab
    mrs = project.mergerequests.list(all=True, **{'iids[]': iids}) if iids else []
    if len(mrs) != len(iids):
        raise RuntimeError("Could not list all {} MRs, got {}"
                           .format(len(iids), len(mrs)))
    return mrs


def find_project_name(repo):
    '''
    Find the GitLab full project name given a git repository.

    The project name is infered from the url of the 'origin' remote.
    '''
    remotes = git_o(['remote', '-v'], cwd=repo)
    for remote in remotes.splitlines():
        m = re.match(
            r'^origin\s+.*gitlab\.cern\.ch.*/([^/]+/[^/]+)\.git',
            remote)
        if m:
            return m.group(1)
    logging.error('Could not find gitlab project with `git remote -v`.')
    sys.exit(1)

def find_merge_requests(project, milestone_title):
    '''
    Find GitLab merge requests with a given milestone.
    '''
    milestones = [m for m in project.milestones.list(search=milestone_title)
                  if m.title == milestone_title]
    if not milestones:
        logging.debug('Milestone {} not found in GitLab project {}'
                      .format(milestone_title, project.name))
        return []
    elif len(milestones) > 1:
        logging.error('Multiple milestones {} found in GitLab project {}'
                      .format(milestone_title, project.name))
        sys.exit(1)

    milestone = milestones[0]
    return list(milestone.merge_requests())


def get_template(template, template_paths):
    '''
    Return a jinja2.Template from a name and a search path list.

    Three useful functions are added to the environment such that
    they can be used in the template:
    - select_mrs: filter MRs based on labels,
    - mdindent: indent a block of text the markdown way,
    - find_tasks: find JIRA task IDs in the MR description and title.
    '''
    def select_mrs(mrs, labels, used=None):
        '''
        Yield unused MRs that match some lables.

        `labels` can be of the form `['one', ['two', 'three']]`,
        which will match any MR that "has 'one' or (has 'two' and has
        'three')". `labels=[[]]` will match everything.
        '''
        for mr in mrs:
            if used is not None and mr.id in used:
                continue
            if any(set([ls] if isinstance(ls, str) else ls)
                   .issubset(mr.labels) for ls in labels):
                if used is not None:
                    used.append(mr.id)
                yield mr

    def do_mdindent(s, width=2, indentfirst=False):
        return '  \n'.join(width * (indentfirst or i > 0) * ' ' + line
                           for i, line in enumerate(s.splitlines()))

    def find_tasks(mr):
        pattern = r'[A-Z]+-[0-9]+'
        tasks = sorted(set(re.findall(pattern, mr.title) +
                           re.findall(pattern, mr.description)))
        return '[{}]'.format(','.join(tasks)) if tasks else ''

    env = Environment(
        autoescape=False,
        loader=FileSystemLoader(template_paths),
        trim_blocks=False)
    env.globals['select_mrs'] = select_mrs
    env.filters['mdindent'] = do_mdindent
    env.globals['find_tasks'] = find_tasks

    return env.get_template(template)


def main():
    parser = argparse.ArgumentParser(
        description='Generate release notes draft.',
        epilog='''
Example:
  Change directory to a full project clone, checkout the release branch
  and call %(prog)s:

    $ git clone https://:@gitlab.cern.ch:8443/lhcb/Hlt.git
    $ cd Hlt
    $ git checkout -b v27r0-release master  # assuming release from master
    $ %(prog)s v26r6 v27r0

  The project template `ReleaseNotes/release_notes_template.md` is used
  if it exists and otherwise a default template is taken. The draft
  release notes are written under `ReleaseNotes/` by default.
''',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument('previous', help='Previous (base) release')
    parser.add_argument('target', help='Target release')
    parser.add_argument('-t', '--template',
                        default='release_notes_template.md',
                        help='Template filename (searched in {repo}/ReleaseNotes and LbScripts)')
    parser.add_argument('-o', '--output', default='{repo}/ReleaseNotes/{target}{ext}',
                        help='Output file')
    parser.add_argument('-C', '--repo', default='.', help='Path to git repo')
    # branch?
    parser.add_argument('--token', help='GitLab access token (defaults to $GITLAB_TOKEN)')
    parser.add_argument('--debug', action='store_true', help='Increase verbosity')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    template_paths = [os.path.join(args.repo, 'ReleaseNotes'),
                      os.path.join(os.path.dirname(__file__), 'templates')]
    logging.debug('Searching for templates in {}'.format(template_paths))

    args.output = args.output.format(repo=args.repo, target=args.target,
                                     ext=os.path.splitext(args.template)[1])

    if os.path.exists(args.output):
        logging.error('Output {} exists, aborting...'.format(args.output))
        sys.exit(1)
    if not args.token:
        try:
            args.token = os.environ['GITLAB_TOKEN']
        except KeyError:
            logging.error(
                'Either set $GITLAB_TOKEN or use --token.\nA token can be '
                'obtained from https://gitlab.cern.ch/profile/personal_access_tokens')
            sys.exit(1)

    template = get_template(args.template, template_paths)
    print('Using template {}'.format(template.filename))

    project_fullname = find_project_name(args.repo)
    server = gitlab.Gitlab('https://gitlab.cern.ch/', args.token)
    project = server.projects.get(project_fullname)
    git_mrs = find_merge_requests_git(project, args.repo, args.previous)
    gitlab_mrs = find_merge_requests(project, args.target)
    logging.debug('Found these MRs in git history: {}'.format(git_mrs))
    logging.debug('Found these MRs in GitLab: {}'.format(gitlab_mrs))

    if not gitlab_mrs:
        logging.warning('No merge requests found with {} milestone'
                        .format(args.target))
    else:
        # Cross-check git repo with GitLab
        for mr in git_mrs:
            if mr.id not in [x.id for x in gitlab_mrs]:
                logging.warning('Milestone not set for MR {}'
                                .format(mr.web_url))
        for mr in gitlab_mrs:
            if mr.id not in [x.id for x in git_mrs]:
                logging.warning('MR {} is not merged in current branch '
                                'after tag {} (state {})'
                                .format(mr.web_url, args.previous, mr.state))
                git_mrs.append(mr)

    context = {
        'project': project_fullname.split('/')[-1],
        'version': args.target,
        'date': datetime.date.today(),
        'merge_requests': git_mrs,
    }
    with open(args.output, 'w') as f:
        f.write(template.render(context).encode('utf8'))
    print('Release notes draft written to {}.'.format(args.output))
