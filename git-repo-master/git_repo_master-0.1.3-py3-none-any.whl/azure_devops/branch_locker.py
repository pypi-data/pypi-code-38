from git_repo_master.azure_devops.request import AzureGitRequest


class BranchLocker:
    def __init__(self, organization, project, token):
        self.__request = AzureGitRequest() \
            .with_organization(organization) \
            .with_project(project) \
            .with_resource('refs') \
            .with_token(token) \
            .with_method('PATCH')

    def update_branch(self, repository, branch_name='master', is_locked=True):
        self.__request \
            .with_repository(repository) \
            .with_query('filter=heads/{}'.format(branch_name)) \
            .with_body({
                'isLocked': is_locked
            }) \
            .execute()

    def lock_master(self, repository):
        self.update_branch(repository, 'master', True)

    def unlock_master(self, repository):
        self.update_branch(repository, 'master', False)


def lock_branch(args):
    locker = BranchLocker(
        args.organization,
        args.project,
        args.token
    )
    for repo in args.repository:
        locker.update_branch(
            repo,
            branch_name=args.branch,
            is_locked=True
        )


def unlock_branch(args):
    locker = BranchLocker(
        args.organization,
        args.project,
        args.token
    )
    for repo in args.repository:
        locker.update_branch(
            repo,
            branch_name=args.branch,
            is_locked=False
        )
