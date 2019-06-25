from git_repo_master.azure_devops.branch_locker import lock_branch, unlock_branch
from git_repo_master.azure_devops.pull_request_creator import create_pull_request

ACTIONS = {
    'lock-branch': lock_branch,
    'unlock-branch': unlock_branch,
    'create-pull-request': create_pull_request
}
