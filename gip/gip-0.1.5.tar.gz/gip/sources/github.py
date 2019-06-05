import pathlib
import github3

from gip import logger
from gip import exceptions
from gip.sources import base

LOG = logger.get_logger(__name__)


class Github(base.Source):
    """
    Github source
    """

    def __init__(self, repo, version, token):
        """
        Inits Github source

        :param repo: url to repository
        :param version: Tag, branch name or commit sha, defaults to master
        :param token: github api token
        :raise exceptions.AuthenticationError: could not authenticate
        :raise exceptions.HttpError: could not connect
        :raise exceptions.RepoNotFound: repository not found
        """
        # Set version
        self.version = version or 'master'

        # Init Github object
        try:
            self.gh = github3.login(token=token)
        except github3.exceptions.AuthenticationFailed:
            raise exceptions.AuthenticationError(url="https://github.com")

        # Get repository from Gitlab API
        try:
            self.repository = self.gh.repository(
                owner=self.get_owner(repo),
                repository=self.get_repo_name(repo)
            )
        except github3.exceptions.ConnectionError:
            raise exceptions.HttpError(url=repo)
        except github3.exceptions.NotFoundError:
            raise exceptions.RepoNotFound(repo=repo)

    def get_archive(self, dest):
        """
        Downloads archive in dest_dir

        :param dest: path where to download the archive to
        :raise exceptions.DirectoryDoesNotExist: destination dir does not exist
        :raise exceptions.ArchiveNotFound: archive not found
        """
        # Raise error when destination directory does not exists
        dest = pathlib.Path(dest)
        if not dest.parent.is_dir():
            raise exceptions.DirectoryDoesNotExist(dest)

        # Download repository archive to dest
        result = self.repository.archive(
            format='tarball',
            path=dest,
            ref=self.version
        )
        if result is False:
            raise exceptions.ArchiveNotFound(
                repo=self.repository.clone_url,
                version=self.version
            )

    def get_owner(self, url):
        """
        Get owner name from repo url

        :param url: url to repository
        :return: repository owner
        """
        # Split owner from url
        owner = url.split("/")[3]
        return owner

    def get_repo_name(self, url):
        """
        Get repo name from repo url

        :param url: url to repository
        :return: repository name
        """
        if url[-4:] == ".git":
            # Remove .git from url
            url = url[:-4]
        # Split repo_name from url
        repo_name = url.split("/")[4]
        return repo_name

    def get_commit_hash(self):
        """
        Get commit hash for this source

        :return: commit hash for source
        """
        commits = self.repository.commits(
            sha=self.version,
            number=1
        )
        # Get first and only (number=1) item from iterator
        commit = next(commits)
        return commit.sha
