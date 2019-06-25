from git_repo_master.azure_devops.request import AzureGitRequest


class PullRequestCreator:
    def __init__(self, organization, project, token):
        self.__request = AzureGitRequest() \
            .with_organization(organization) \
            .with_project(project) \
            .with_resource('pullrequests') \
            .with_token(token) \
            .with_method('POST')

    def create_pull_request(self,
                            repository,
                            source_branch,
                            target_branch,
                            title,
                            description):
        self.__request \
            .with_repository(repository) \
            .with_body({
                "sourceRefName": "refs/heads/{}".format(source_branch),
                "targetRefName": "refs/heads/{}".format(target_branch),
                "title": title,
                "description": description,
            }) \
            .execute()


def create_pull_request(args):
    creator = PullRequestCreator(
        args.organization,
        args.project,
        args.token
    )
    for repo in args.repository:
        creator.create_pull_request(
            repo,
            args.source,
            args.target,
            args.title,
            args.description
        )

