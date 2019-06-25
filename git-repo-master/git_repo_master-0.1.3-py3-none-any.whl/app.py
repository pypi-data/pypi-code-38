from git_repo_master.azure_actions import ACTIONS
from git_repo_master.parser import startup_parser


def run():
    args = startup_parser()
    if args.action in ACTIONS:
        ACTIONS[args.action](args)
    else:
        print('Nothing to do.')
