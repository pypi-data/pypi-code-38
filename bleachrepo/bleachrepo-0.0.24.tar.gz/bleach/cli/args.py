import sys
import argparse

from bleach import config


def getCommandlineArgs():
    parser = argparse.ArgumentParser(prog="bleach", description="Keep your repository clean and tidy")

    parser.add_argument("owner", help="the name of the repository's owner")
    parser.add_argument("repository", help="the name of the repository to get PR status for")
    parser.add_argument("--outputMethod", help="output method. may be 'stdout' (default) or 'slack'"
                                               " (requires OAuth token)", default=config.DEFAULT_OUTPUT_METHOD)
    parser.add_argument(
        "--sourceControl",
        help="type of source control to query. currently supported: GitHub, BitBucket (Cloud)."
             " valid values are 'github' or 'bitbucket'. defaults to github."
             "if you choose 'github', you must provide an access token in order to access private repositories."
             " this is possible by setting the environment variable BLEACH_GITHUB_ACCESS_TOKEN"
             "if you choose 'bitbucket', you must provide username and password (or App Password)."
             " this is possible by setting the environment variables BLEACH_BITBUCKET_CLOUD_USER"
             " and BLEACH_BITBUCKET_CLOUD_PASSWORD",
        default=config.DEFAULT_SOURCE_CONTROL,
    )

    subparsers = parser.add_subparsers(help='sub-command help', dest='subparser_name')
    subparserPullrequest = subparsers.add_parser('pr', help='check pull request age')
    subparserBranchDiscrepancy = subparsers.add_parser('branch', help='compare branches')

    subparserPullrequest.add_argument("--daysOpenThreshold", help="show only pull requests open longer than this number (days)",
                        type=int, default=config.CONFIG['daysOpenThreshold'])
    subparserPullrequest.add_argument("--countToDisplay", help="how many pull requests to display", type=int,
                        default=config.CONFIG['countToDisplay'])

    subparserBranchDiscrepancy.add_argument("primary", help="name of the primary branch")
    subparserBranchDiscrepancy.add_argument("secondary", help="name of the secondary branch")

    args = parser.parse_args()
    _validateArgs(args)
    _loadArgsToConfig(args)
    return args


def _validateArgs(args):
    # use types for validation
    # https://stackoverflow.com/questions/14117415/in-python-using-argparse-allow-only-positive-integers
    # TODO restore me omfg
    return

    if args.daysOpenThreshold < 0:
        print("--daysOpenThreshold must be non-negative")
        sys.exit(1)

    if args.countToDisplay < 0:
        print("--countToDisplay must be non-negative")
        sys.exit(1)

    if args.outputMethod not in ['slack', 'stdout']:
        print("--outputMethod must be stdout or slack")
        sys.exit(1)

    if args.outputMethod == 'slack':
        if not config.CONFIG['slackWebhook']:
            print("must set a slack webhook using environment variable BLEACH_SLACK_WEBHOOK")
            sys.exit(1)

    if args.sourceControl not in ['github', 'bitbucket']:
        print("--sourceControl must be github or bitbucket")
        sys.exit(1)

    if args.sourceControl == 'bitbucket':
        if not config.CONFIG['bitbucketCloudUser']:
            print("must set the bitbucket cloud username using environment variable BLEACH_BITBUCKET_CLOUD_USER")
            sys.exit(1)
        if not config.CONFIG['bitbucketCloudPassword']:
            print("must set the bitbucket cloud password using environment variable BLEACH_BITBUCKET_CLOUD_PASSWORD")
            sys.exit(1)


def _loadArgsToConfig(args):
    # this is terrible
    if (args.subparser_name == 'pr'):
        config.CONFIG["daysOpenThreshold"] = args.daysOpenThreshold
        config.CONFIG["countToDisplay"] = args.countToDisplay

    if (args.subparser_name == 'branch'):
        config.CONFIG["primary"] = args.primary
        config.CONFIG["secondary"] = args.secondary

    config.CONFIG["outputMethod"] = args.outputMethod
    config.CONFIG["sourceControl"] = args.sourceControl
