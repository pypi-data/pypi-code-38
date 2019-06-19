#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Utilities for retrieving, parsing and auto-generating changelogs'''

import io
import datetime

import pytz
import dateutil.parser

from .log import get_logger
logger = get_logger(__name__)


def parse_date(d):
    '''Parses any date supported by :py:func:`dateutil.parser.parse`'''

    return dateutil.parser.parse(d, ignoretz=True).replace(
                tzinfo=pytz.timezone("Europe/Zurich"))


def _sort_commits(commits, reverse):
    '''Sorts gitlab commit objects using their ``committed_date`` attribute'''

    return sorted(commits,
        key=lambda x: parse_date(x.committed_date),
        reverse=reverse,
        )


def _sort_tags(tags, reverse):
    '''Sorts gitlab tag objects using their ``committed_date`` attribute'''

    return sorted(tags,
        key=lambda x: parse_date(x.commit['committed_date']),
        reverse=reverse,
        )


def get_file_from_gitlab(gitpkg, path, ref='master'):
    '''Retrieves a file from a Gitlab repository, returns a (StringIO) file'''

    return io.StringIO(gitpkg.files.get(file_path=path, ref=branch).decode())


def get_last_tag(package):
    '''Returns the last (gitlab object) tag for the given package

    Args:

        package: The gitlab project object from where to fetch the last release
                 date information


    Returns: a tag object
    '''

    # according to the Gitlab API documentation, tags are sorted from the last
    # updated to the first, by default - no need to do further sorting!
    tag_list = package.tags.list()

    if tag_list:
        # there are tags, use these
        return tag_list[0]


def get_last_tag_date(package):
    '''Returns the last release date for the given package

    Falls back to the first commit date if the package has not yet been tagged


    Args:

        package: The gitlab project object from where to fetch the last release
                 date information


    Returns: a datetime object that refers to the last date the package was
             released.  If the package was never released, then returns the
             date just before the first commit.
    '''

    # according to the Gitlab API documentation, tags are sorted from the last
    # updated to the first, by default - no need to do further sorting!
    tag_list = package.tags.list()

    if tag_list:
        # there are tags, use these
        last = tag_list[0]
        logger.debug('Last tag for package %s (id=%d) is %s', package.name,
            package.id, last.name)
        return parse_date(last.commit['committed_date']) + \
            datetime.timedelta(milliseconds=500)

    else:
        commit_list = package.commits.list(all=True)

        if commit_list:
            # there are commits, use these
            first = _sort_commits(commit_list, reverse=False)[0]
            logger.debug('First commit for package %s (id=%d) is from %s',
                package.name, package.id, first.committed_date)
            return parse_date(first.committed_date) - \
                datetime.timedelta(milliseconds=500)

        else:
            # there are no commits nor tags - abort
            raise RuntimeError('package %s (id=%d) does not have commits ' \
                'or tags so I cannot devise a good starting date' % \
                (package.name, package.id))


def _get_tag_changelog(tag):

    try:
        return tag.release['description']
    except Exception:
        return ''


def _write_one_tag(f, pkg_name, tag):
    '''Prints commit information for a single tag of a given package

    Args:

        f: A :py:class:`File` ready to be written at
        pkg_name: The name of the package we are writing tags of
        tag: The tag value

    '''

    git_date = parse_date(tag.commit['committed_date'])
    f.write('  * %s (%s)\n' % (tag.name,  git_date.strftime('%b %d, %Y %H:%M')))

    for line in _get_tag_changelog(tag).replace('\r\n', '\n').split('\n'):

        line = line.strip()
        if line.startswith('* ') or line.startswith('- '):
            line = line[2:]

        line = line.replace('!', pkg_name + '!').replace(pkg_name + \
            pkg_name, pkg_name)
        line = line.replace('#', pkg_name + '#')
        if not line:
            continue
        f.write('%s* %s' % (5*' ', line))


def _write_commits_range(f, pkg_name, commits):
    '''Writes all commits of a given package within a range, to the output file

    Args:

        f: A :py:class:`File` ready to be written at
        pkg_name: The name of the package we are writing tags of
        commits: List of commits to be written

    '''


    for commit in commits:
        commit_title = commit.title

        # skip commits that do not carry much useful information
        if '[skip ci]' in commit_title or \
                        'Merge branch' in commit_title or \
                        'Increased stable' in commit_title:
            continue

        commit_title = commit_title.strip()
        commit_title = commit_title.replace('!', pkg_name + '!').replace(pkg_name + pkg_name, pkg_name)
        commit_title = commit_title.replace('#', pkg_name + '#')
        f.write('%s- %s\n' % (' ' * 5, commit_title))


def _write_mergerequests_range(f, pkg_name, mrs):
    '''Writes all merge-requests of a given package, with a range, to the
    output file

    Args:

        f: A :py:class:`File` ready to be written at
        pkg_name: The name of the package we are writing tags of
        mrs: The list of merge requests to write

    '''

    for mr in mrs:
        title = mr.title.strip().replace('\r','').replace('\n', '  ')
        title = title.replace(' !', ' ' + pkg_name + '!')
        title = title.replace(' #', ' ' + pkg_name + '#')
        if mr.description is not None:
          description = \
              mr.description.strip().replace('\r','').replace('\n', '  ')
          description = description.replace(' !', ' ' + pkg_name + '!')
          description = description.replace(' #', ' ' + pkg_name + '#')
        else:
          description = 'No description for this MR'
        space = ': ' if description else ''
        log = '''     - {pkg}!{iid} {title}{space}{description}'''
        f.write(log.format(pkg=pkg_name, iid=mr.iid, title=title, space=space, description=description))
        f.write('\n')


def write_tags_with_commits(f, gitpkg, since, mode):
    '''Writes all tags and commits of a given package to the output file

    Args:

        f: A :py:class:`File` ready to be written at
        gitpkg: A pointer to the gitlab package object
        since: Starting date (as a datetime object)
        mode: One of mrs (merge-requests), commits or tags indicating how to
              list entries in the changelog for this package

    '''

    # get tags since release and sort them
    tags = gitpkg.tags.list()

    # sort tags by date
    tags = [k for k in tags if parse_date(k.commit['committed_date']) >= since]
    tags = _sort_tags(tags, reverse=False)

    # get commits since release date and sort them too
    commits = gitpkg.commits.list(since=since, all=True)

    # sort commits by date
    commits = _sort_commits(commits, reverse=False)

    # get merge requests since the release data
    mrs = list(reversed(gitpkg.mergerequests.list(state='merged', updated_after=since, order_by='updated_at', all=True)))
    f.write('* %s\n' % (gitpkg.attributes['path_with_namespace'],))

    # go through tags and writes each with its message and corresponding
    # commits
    start_date = since
    for tag in tags:

        # write tag name and its text
        _write_one_tag(f, gitpkg.attributes['path_with_namespace'], tag)
        end_date = parse_date(tag.commit['committed_date'])

        if mode == 'commits':
            # write commits from the previous tag up to this one
            commits4tag = [k for k in commits \
                if (start_date < parse_date(k.committed_date) <= end_date)]
            _write_commits_range(f, gitpkg.attributes['path_with_namespace'],
                commits4tag)

        elif mode == 'mrs':
            # write merge requests from the previous tag up to this one
            # the attribute 'merged_at' is not available in GitLab API as of 27
            # June 2018
            mrs4tag = [k for k in mrs \
                if (start_date < parse_date(k.updated_at) <= end_date)]
            _write_mergerequests_range(f,
                gitpkg.attributes['path_with_namespace'], mrs4tag)

        start_date = end_date

    if mode != 'tags':

        # write the tentative patch version bump for the future tag
        f.write('  * patch\n')

        if mode == 'mrs':
            # write leftover merge requests
            # the attribute 'merged_at' is not available in GitLab API as of 27
            # June 2018
            leftover_mrs = [k for k in mrs \
                if parse_date(k.updated_at) > start_date]
            _write_mergerequests_range(f,
                gitpkg.attributes['path_with_namespace'], leftover_mrs)

        else:
            # write leftover commits that were not tagged yet
            leftover_commits = [k for k in commits \
                if parse_date(k.committed_date) > start_date]
            _write_commits_range(f, gitpkg.attributes['path_with_namespace'],
                leftover_commits)


def write_tags(f, gitpkg, since):
    '''Writes all tags of a given package to the output file

    Args:

        f: A :py:class:`File` ready to be written at
        gitpkg: A pointer to the gitlab package object
        since: Starting date as a datetime object

    '''

    tags = gitpkg.tags.list()
    # sort tags by date
    tags = [k for k in tags if parse_date(k.commit['committed_date']) >= since]
    tags = _sort_tags(tags, reverse=False)
    f.write('* %s\n')

    for tag in tags:
        _write_one_tag(gitpkg.attributes['path_with_namespace'], tag)
