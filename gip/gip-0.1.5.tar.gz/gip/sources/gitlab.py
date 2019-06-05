import gitlab
import pathlib
from urllib.parse import urlsplit

from gip import logger
from gip import exceptions
from gip.sources import base

LOG = logger.get_logger(__name__)


class Gitlab(base.Source):
    """ Gitlab source """

    def __init__(self, repo, version, token):
        """
        Inits Gitlab source

        :param repo: url to repository
        :param version: Tag, branch name or commit sha, defaults to master
        :param token: gitlab api token
        :raise exceptions.AuthenticationError: could not authenticate
        :raise exceptions.HttpError: could not connect
        :raise exceptions.RepoNotFound: repository not found
        """
        # Set version
        self.version = version or 'master'

        # Init Gitlab connection
        try:
            self.gl = gitlab.Gitlab(
                url=self._get_base_url(repo),
                private_token=token
            )
        except gitlab.GitlabAuthenticationError:
            raise exceptions.AuthenticationError(url=repo)
        except gitlab.GitlabHttpError as e:
            raise exceptions.HttpError(url=repo, code=e.response_code)

        # Split project_path from passed repo url
        project_path = self._get_project_path(repo)

        # Get project from Gitlab API as object
        try:
            self.project = self.gl.projects.get(project_path)
        except gitlab.exceptions.GitlabGetError:
            raise exceptions.RepoNotFound(repo)

    def get_archive(self, dest):
        """
        Downloads archive in dest_dir

        :param dest: path where to download the archive to
        :raise exceptions.DirectoryDoesNotExist: destination dir does not exist
        :raise exceptions.AuthenticationError: could not authenticate
        :raise exceptions.ArchiveNotFound: archive not found
        """
        # Raise error when destination directory does not exists
        dest = pathlib.Path(dest)
        if not dest.parent.is_dir():
            raise exceptions.DirectoryDoesNotExist(dest)

        # Get project archive
        try:
            with open(dest, "wb") as f:
                self.project.repository_archive(
                    sha=self.version, streamed=True, action=f.write)
        except FileNotFoundError:
            raise exceptions.DirectoryDoesNotExist(dest)
        except gitlab.GitlabAuthenticationError:
            raise exceptions.AuthenticationError(url=self.project.web_url)
        except gitlab.GitlabListError:
            raise exceptions.ArchiveNotFound(
                repo=self.project.web_url,
                version=self.version
            )

    def get_commit_hash(self):
        """
        Get commit hash for this source

        :return: commit hash for source
        """
        commits = self.project.commits.list(ref_name=self.version)
        try:
            return commits[0].id
        except IndexError:
            raise exceptions.CommitHashNotFound(
                repo=self.project.web_url,
                version=self.version
            )

    def _get_project_path(self, repo):
        """
        Get project path of repo url

        :return: project path of source
        """
        # Removes leading slash
        path = urlsplit(repo).path[1:]
        if path[-4:] == ".git":
            # Remove .git from URL
            path = path[:-4]
        return path

    def _get_base_url(self, repo):
        """
        Get base url of repository url

        :return: base url of Gitlab instance
        """
        # Split repo url in parts
        split_url = urlsplit(repo)
        return "{0}://{1}".format(split_url.scheme, split_url.netloc)
