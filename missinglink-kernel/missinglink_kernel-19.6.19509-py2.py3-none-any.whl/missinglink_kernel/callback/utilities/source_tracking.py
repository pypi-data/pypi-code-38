from __future__ import print_function, division
import hashlib
import logging
import re
import tempfile
from datetime import datetime
from os import path, remove
from shutil import copyfile, rmtree, copytree
from traceback import format_exception_only
from six.moves.urllib import parse
import os
import sys
import errno

logger = logging.getLogger('missinglink')


def export_exception(ex):
    return ('\n'.join(format_exception_only(ex.__class__, ex))).strip()


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class GitError(Exception):
    pass


class GitExpando(object):
    pass


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def _append_commit_link(remote_template):
    x = parse.urlparse(remote_template)
    if x.hostname is not None:
        remote_template += '/commit/{}' if x.hostname.lower() == 'github.com' else '/commits/{}'
    return remote_template


def __remote_to_template(remote_url):
    remote_template = remote_url
    if '@' in remote_template:
        remote_template = 'https://' + (remote_url.split('@')[1].strip()).replace(':', '/')
    remote_template = remote_template if not remote_url.lower().endswith('.git') else remote_template[:-4]
    return _append_commit_link(remote_template)


def __validate_remote(res):
    if res.remote_url is None:
        logger.warning('Repository has no remote')
        raise GitError('Repository has no remote')


def __fill_repo(repo, res=GitExpando()):
    res.repo = repo
    res.git_version = repo.git.version()
    res.remote_name = None
    res.remote_url = None
    res.has_head = repo.head.is_valid()
    res._remote_template = None
    if len(repo.remotes) > 0:
        remote = list(repo.remotes)[0]
        res.remote_name = remote.name
        res.remote_url = remote.url
        res._remote_template = __remote_to_template(remote.url)
    __validate_remote(res)
    res.branch = repo.active_branch
    res.head_sha = res.repo.head.object.hexsha if res.has_head else None

    res.head_sha_url = res._remote_template.format(
        res.head_sha) if res._remote_template and res.head_sha else res.head_sha
    res.is_clean = repo.git.status(porcelain=True).strip() == ''
    return res


def _export_commit(commit):
    return {'author': commit.author.name,
            'email': commit.author.email,
            'date': commit.authored_datetime.isoformat()}


def import_git():
    try:
        import git
        return git
    except ImportError:
        logger.warning('Failed to import git')
        raise GitError('Failed to import git')


def get_repo(path_='.', repo=None):
    git = import_git()
    try:
        repo = repo or git.Repo(path_, search_parent_directories=True)
        response = __fill_repo(repo)
        response.export_commit = _export_commit
        response.refresh = lambda: __fill_repo(repo, response)
        return response
    except git.exc.InvalidGitRepositoryError:
        logger.warning('path is not tracked')
        raise GitError('path is not tracked')


class GitRepoSyncer(object):
    SYNC_FILE_THRESHOLD = 5242880  # 5 MB

    @classmethod
    def _sanitize_branch_name(cls, name):
        return re.sub(r"[^a-zA-Z0-9/]", "_", name)

    @classmethod
    def _raise_git_error_if(cls, condtition, *args, **kwargs):
        if condtition:
            raise GitError(*args, **kwargs)

    @classmethod
    def try_ex_path(cls, git, repo_path, remote_url):
        if path.isdir(repo_path):
            try:
                repo = git.Repo(repo_path)
                remotes = cls._get_remotes(repo)
                cls._raise_git_error_if('origin' not in remotes, 'The tracking repository origin is not present')
                origin_remote = remotes['origin']
                cls._raise_git_error_if(origin_remote.url != remote_url,
                                        'The tracking repository origin is broken: %s != %s', origin_remote.url,
                                        remote_url)
                return repo
            except Exception as ex:
                logger.warning("Tracking repository repo at {} is reset due to: {}".format(repo_path, str(ex)))
                rmtree(repo_path)
        return None

    @classmethod
    def _get_remotes(cls, repo):
        return {x.name: x for x in repo.remotes}

    @classmethod
    def _validate_tracking_repository_or_clone(cls, repo_path, tracking_origin_url):
        git = import_git()
        repo = cls.try_ex_path(git, repo_path, tracking_origin_url) or git.Repo.clone_from(tracking_origin_url,
                                                                                           repo_path)
        repo.git.reset(hard=True)
        repo.git.clean('-qfdx')
        return repo

    @classmethod
    def get_repo_path_hash(cls, url):
        return hashlib.sha256(url.encode('utf-8')).hexdigest()[:7]

    @classmethod
    def _get_remote_path(cls, tracking_repository_remote_url):
        repo_id = 'ml_{}_{}'.format(cls.get_repo_path_hash(os.path.expanduser('~')),
                                    cls.get_repo_path_hash(tracking_repository_remote_url))
        return path.join(tempfile.gettempdir(), repo_id)

    @classmethod
    def clone_tracking_repo(cls, tracking_repository_remote_url):
        temp_path = cls._get_remote_path(tracking_repository_remote_url)
        logger.debug("Clone {} to {}".format(tracking_repository_remote_url, temp_path))
        return cls._validate_tracking_repository_or_clone(temp_path, tracking_repository_remote_url)

    @classmethod
    def _checkout(cls, repo, branch=None):
        repo.git.rm('-r', '--cached', '--ignore-unmatch', '.')
        repo.git.clean('-qfdx')

        if branch in repo.branches:
            repo.git.checkout(branch)
        else:
            repo.git.checkout(orphan=branch)

        repo.git.rm('-r', '--cached', '--ignore-unmatch', '.')
        repo.git.clean('-qfdx')

    @classmethod
    def _warn_big_file(cls, file_mode, file_path):

        if file_mode in ['D', 'R', 'C']:  # deleted, renamed, copied
            logger.debug('File %s mode is %s, skipping size check', file_path, file_mode)
            return

        if not path.exists(file_path):
            logger.warning('File %s (%s) not found', file_path, file_mode)
            return

        fsize = path.getsize(file_path)
        if fsize > cls.SYNC_FILE_THRESHOLD:
            eprint('Repository Tracking: The file %s is big (%s MB). You might want to add it to .gitignore' % (
                file_path, round(fsize / (1024 * 1024))))

    @classmethod
    def _warn_big_files(cls, repo):
        for change in repo.git.status(porcelain=True, untracked_files='all').strip().split('\n'):
            mode, rel_path = [x.strip() for x in change.strip().split(' ', 1)]
            file_path = path.join(repo.working_dir, rel_path)
            cls._warn_big_file(mode, file_path)

    @classmethod
    def _get_changed_files(cls, repo):
        changes = repo.git.status(porcelain=True, untracked_files='all').strip()
        if len(changes) == 0:
            return []

        cls._warn_big_files(repo)

        files = map(lambda x: x.split(' ')[-1].strip(), changes.split('\n'))
        return list(files)

    @classmethod
    def copyfile(cls, src_file, tracked_file):
        parent_dir = os.path.abspath(os.path.join(tracked_file, path.pardir))
        if not os.path.exists(parent_dir):
            mkdir_p(parent_dir)

        return copyfile(src_file, tracked_file)

    @classmethod
    def _copy_path(cls, src_file, tracked_file):
        if not path.exists(src_file):
            return False

        if path.isdir(src_file):
            if path.exists(tracked_file):
                rmtree(tracked_file, ignore_errors=True)

            copytree(src_file, tracked_file)
            return True

        cls.copyfile(src_file, tracked_file)
        return True

    @classmethod
    def _remove_path(cls, tracked_file):
        if not path.exists(tracked_file):  # the file is deleted - delete it
            return

        if path.isdir(tracked_file):
            rmtree(tracked_file)
            return

        remove(tracked_file)
        return

    @classmethod
    def _sync_uncommitted_changes(cls, src, tracking):
        changed_files = cls._get_changed_files(src)
        for changed_file in changed_files:
            src_file = path.join(src.working_dir, changed_file)
            tracked_file = path.join(tracking.working_dir, changed_file)
            logger.debug('_sync_uncommitted_changes %s -> %s', src_file, tracked_file)

            if not cls._copy_path(src_file, tracked_file):  # the file is present, copy it...
                cls._remove_path(tracked_file)

        if len(changed_files) > 0:
            tracking.git.add('.')
            tracking.index.commit(
                'ML AI: Synced file(s) from {}.Files: \n{}'.format(src.working_dir, '\n'.join(changed_files)))

    @classmethod
    def _cp_lfs(cls, src, tracking, branch_name):
        import shutil

        src_lfs_path = path.join(src.git_dir, 'lfs')
        tracking_lfs_path = path.join(tracking.git_dir, 'lfs')
        if path.isdir(src_lfs_path):
            logger.info('LFS cache found in source repository. Syncing %s to %s', src_lfs_path, tracking_lfs_path)
            if path.isdir(tracking_lfs_path):
                logger.debug('Remove shadow LFS dir %s', tracking_lfs_path)
                shutil.rmtree(tracking_lfs_path)
            shutil.copytree(src_lfs_path, tracking_lfs_path)

    @classmethod
    def _merge_to_new_branch(cls, src, tracking, branch_name):
        git = import_git()

        tracking.git.fetch('origin')
        cls._cp_lfs(src, tracking, branch_name)
        tracking.git.fetch('src')
        cls._checkout(tracking, branch_name)
        if src.head.is_valid():
            try:
                tracking.git.merge('src/{}'.format(src.active_branch), allow_unrelated_histories=True)
            except git.exc.GitCommandError:
                tracking.git.merge('src/{}'.format(src.active_branch))

            return True
        return False

    @classmethod
    def _push_to_tracking_repository_remote(cls, tracking_repository):
        if not tracking_repository.head.is_valid():
            tracking_repository.git.commit(m='empty commit', allow_empty=True)
        tracking_repository.remotes['origin'].push(
            '{}:{}'.format(tracking_repository.active_branch, tracking_repository.active_branch))

    @classmethod
    def merge_src_to_tracking_repository(cls, src, tracking_repository):
        git = import_git()
        src_remote = git.Remote(tracking_repository, 'src')
        if src_remote.exists():
            tracking_repository.delete_remote(src_remote)

        tracking_repository.create_remote('src', src.git_dir)
        br_tag = '{}'.format(datetime.utcnow())

        br_name = cls._sanitize_branch_name('{}_/{}'.format(src.active_branch, br_tag))
        cls._merge_to_new_branch(src, tracking_repository, br_name)
        cls._sync_uncommitted_changes(src, tracking_repository)
        cls._push_to_tracking_repository_remote(tracking_repository)
        return br_name

    @classmethod
    def source_tracking_data(cls, path_='.'):
        repo_obj = None
        src_data = {}
        try:
            repo_obj = get_repo(path_=path_)
            src_data = cls.export_repo_state()
        # noinspection PyBroadException
        except Exception as ex:
            src_data['error'] = export_exception(ex)

        return src_data, repo_obj

    @classmethod
    def export_repo_state(cls, repo_obj=None):

        src_data = {}
        try:
            repo_obj = repo_obj or get_repo()

            src_data['branch'] = repo_obj.branch.name
            src_data['remote'] = repo_obj.remote_url
            src_data['sha_local'] = repo_obj.head_sha
            src_data['sha_local_url'] = repo_obj.head_sha_url
            src_data['is_dirty'] = not repo_obj.is_clean

            commit_data = None
            if repo_obj.has_head:
                commit_data = repo_obj.export_commit(repo_obj.repo.head.commit)

            if commit_data is not None:
                src_data.update(commit_data)

        # noinspection PyBroadException
        except Exception as ex:
            src_data['error'] = export_exception(ex)

        return src_data

    @classmethod
    def sync_working_dir_if_needed(cls, repo_obj, in_rm_context=False):
        from git import GitCommandError

        try:
            if in_rm_context:
                logger.info('repository tracking not active: running in resource manager context.')
                return {'error': 'running in resource manager context. shadow tracking does not apply'}

            shadow_url = cls.get_shadow_repo(repo_obj)
            if shadow_url is None:
                return {'error': 'no tracking repository found.'}

            logger.info('There is repository tracking enabled. Tracking to repository: {}'.format(shadow_url))
            shadow_repo = cls.clone_tracking_repo(shadow_url)
            commit_tag = cls.merge_src_to_tracking_repository(repo_obj.repo, shadow_repo)
            shadow_repo_obj = get_repo(repo=shadow_repo)
            cur_br = shadow_repo.active_branch
            shadow_repo.git.checkout(commit_tag)
            shadow_repo_obj.refresh()
            src_data = cls.export_repo_state(shadow_repo_obj)
            shadow_repo.git.checkout(cur_br)

            if 'error' not in src_data:
                logger.info(
                    'Tracking repository sync completed. This experiment source code is available here: {}'.format(
                        src_data['sha_local_url']))
            else:
                logger.info('Tracking repository sync Failed. The Error was: {}'.format(src_data['error']))

        except GitCommandError as ex:
            ex_txt = cls._parse_git_error(ex)
            logger.error(ex_txt)
            src_data = {'error': ex_txt}

        except Exception as ex:
            error_msg = ("Failed to init repository tracking. This experiment may not be tracked. \n Internal Error: %s" % export_exception(
                ex))
            logger.error(error_msg)
            src_data = {'error': export_exception(ex)}

        return src_data

    @classmethod
    def _parse_git_error(cls, git_exception):
        std_err = git_exception.stderr.partition('strerr: ')[2]
        cmd = git_exception.command
        text = "Failed to init repository tracking. This experiment may not be tracked. Make sure your remote repository is accessible."
        err_msg = "%s\n%s\n%s" % (std_err, cmd, text)
        return err_msg

    @classmethod
    def get_shadow_repo(cls, repo_obj):
        if repo_obj is None:
            return None

        if repo_obj.remote_url is None:
            logger.warning('The git repository in %s has not remote url. Only advanced source tracking is supported.',
                           repo_obj.repo.working_dir)

        tracking_file = path.join(repo_obj.repo.working_dir, '.ml_tracking_repo')
        if path.isfile(tracking_file):
            logger.debug('Found tracking file: {}'.format(tracking_file))

            with open(tracking_file) as f:
                target_repo = f.readline().strip()
                return target_repo

        return None
