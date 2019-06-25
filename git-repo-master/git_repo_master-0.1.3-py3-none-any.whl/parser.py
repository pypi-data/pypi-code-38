import argparse

from git_repo_master.azure_actions import ACTIONS


def startup_parser():
    parser = argparse.ArgumentParser()
    group_all = parser.add_argument_group('All arguments')
    group_all.add_argument('-organization', help='Azure DevOps organization')
    group_all.add_argument('-project', help='Azure DevOps project in given organization')
    group_all.add_argument('-repository', help='Repo for action', nargs='+')
    group_all.add_argument('-token', help='Personal access token for Azure DevOps')
    group_all.add_argument('-action', help='Action to perform', choices=ACTIONS.keys())
    group_lock = parser.add_argument_group("Branch lock and unlock actions arguments")
    group_lock.add_argument('-branch', help='Branch to perform action on')
    group_pull = parser.add_argument_group("Create pull request action arguments")
    group_pull.add_argument('-source', help='Branch name from which action has to be done')
    group_pull.add_argument('-target', help='Branch name to which action has to be done')
    group_pull.add_argument('-title', help='Pull request title')
    group_pull.add_argument('-description', help='Pull request description')

    args = parser.parse_args()
    return args
