import logging
import os
import re
import subprocess

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def githead():
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:40]
    return sha.decode('utf-8')


class CIBase(object):
    ID_ENV = None
    PR_ENV = None
    REPO_ENV = None
    SHA_ENV = None

    def __str__(self):
        return f"TYPE: {str(self.ci_type)} PR: {str(self.pr)} SHA: {str(self.commit_sha)} REPO: {str(self.repo)}"

    def _get_value(self, key):
        if key:
            return os.environ.get(key, None)
        return None

    @property
    def ci_type(self):
        return self.__class__.__name__

    @property
    def pr(self):
        return self._get_value(self.PR_ENV)

    @property
    def repo(self):
        return self._get_value(self.REPO_ENV)

    @property
    def commit_sha(self):
        return self._get_value(self.SHA_ENV)


class Travis(CIBase):
    ID_ENV = "TRAVIS"
    PR_ENV = "TRAVIS_PULL_REQUEST"
    REPO_ENV = "TRAVIS_REPO_SLUG"
    SHA_ENV = "TRAVIS_PULL_REQUEST_SHA"

    @property
    def pr(self):
        pr = self._get_value(self.PR_ENV)
        if pr == 'false':
            return None
        else:
            return pr


class CircleCI(CIBase):
    ID_ENV = "CIRCLECI"
    PR_ENV = "CIRCLE_PR_NUMBER"
    SHA_ENV = "CIRCLE_SHA1"

    @property
    def repo(self):
        username = self._get_value("CIRCLE_PROJECT_USERNAME")
        reponame = self._get_value("CIRCLE_PROJECT_REPONAME")
        if None in [username, reponame]:
            return None

        return "/".join([username, reponame])


class AppVeyor(CIBase):
    ID_ENV = "APPVEYOR"
    PR_ENV = "APPVEYOR_PULL_REQUEST_NUMBER"
    REPO_ENV = "APPVEYOR_REPO_NAME"
    SHA_ENV = "APPVEYOR_REPO_COMMIT"


class Shippable(CIBase):
    ID_ENV = "SHIPPABLE"
    PR_ENV = "PULL_REQUEST"
    REPO_ENV = "SHIPPABLE_REPO_SLUG"
    SHA_ENV = "COMMIT"


class Semaphore(CIBase):
    ID_ENV = "SEMAPHORE"
    PR_ENV = "PULL_REQUEST_NUMBER"
    REPO_ENV = "SEMAPHORE_REPO_SLUG"
    SHA_ENV = "REVISION"


class CodeBuild(CIBase):
    ID_ENV = "CODEBUILD_BUILD_ID"
    PR_ENV = "CODEBUILD_SOURCE_VERSION"
    REPO_ENV = "CODEBUILD_SOURCE_REPO_URL"
    SHA_ENV = None

    REPO_REGEX = r'.+github\.com/(?P<repo>.+\/.+)\.git'

    @property
    def pr(self):
        pr = self._get_value(self.PR_ENV)
        if pr:
            pr = pr.split("/")[1]
        return pr

    @property
    def repo(self):
        REPO_REGEX = r'.+github\.com/(?P<repo>.+\/.+)\.git'
        repo = self._get_value(self.REPO_ENV)
        if repo:
            match = re.match(REPO_REGEX, repo)
            try:
                repo = match.group('repo')
            except:
                pass

        return repo

    @property
    def commit_sha(self):
        return githead()


class AzureDevOps(CIBase):
    ID_ENV = "AZURE_HTTP_USER_AGENT"
    PR_ENV = "SYSTEM_PULLREQUEST_PULLREQUESTNUMBER"
    REPO_ENV = "BUILD_REPOSITORY_ID"
    SHA_ENV = "BUILD_SOURCEVERSION"


def find_ci_provider():
    ci_providers = [Travis, CircleCI, AppVeyor, Shippable, CodeBuild, AzureDevOps]
    for ci_provider in ci_providers:
        if ci_provider.ID_ENV in os.environ:
            LOGGER.info('CI {} detected'.format(ci_provider.__name__))
            return ci_provider()

    LOGGER.info('No CI detected')
    return CIBase()
