import logging

from github3 import GitHub

from .models import Commit

LOGS = logging.getLogger(__name__)


class GitHubClient(GitHub):
    """ github3.py Client wrapper

    This class wraps the github3 client and provides a public api for use in
    OpenStax projects
    """

    def __init__(self, user=None, password=None, token=None):
        super(GitHubClient, self).__init__(user, password, token)

    def find_pr_commits(self, repo_name, base, head):

        org_name = repo_name.split('/')[0]
        repo_name = repo_name.split('/')[1]

        repo = self.repository(org_name, repo_name)

        comparison = repo.compare_commits(base, head)

        _pr_commits = []

        for commit in comparison.commits:
            # Use our commit object
            commit = Commit(commit._json_data, repository=repo)
            LOGS.info(f'Checking commit {commit.sha}')

            if commit.is_pr_commit:
                LOGS.info(commit)
                pr_issue = repo.issue(commit.pr_id)

                if pr_issue.milestone:
                    commit.milestone = pr_issue.milestone.title
                else:
                    commit.milestone = ""

                _pr_commits.append(commit)

        if _pr_commits:
            LOGS.info(f'{len(_pr_commits)} PR commits were returned')
            return _pr_commits
        else:
            return None
