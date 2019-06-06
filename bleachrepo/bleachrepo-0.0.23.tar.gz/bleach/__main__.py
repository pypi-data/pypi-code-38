from bleach.commands import branch
from bleach.commands import pullrequest

from bleach import config
from bleach.cli import args
from bleach.outputs import slack
from bleach.outputs import stdout
from bleach.sourcecontrol import github


if __name__ == "__main__":
    args = args.getCommandlineArgs()

    # parsers can and should use subcommand set_default to invoke the proper command
    # https://docs.python.org/3/library/argparse.html
    # instead of this silly stuff repeating itself
    if args.subparser_name == 'pr':
        pullrequest.main(args.owner, args.repository)

    if args.subparser_name == 'branch':
        branch.main(args.owner, args.repository, args.primary, args.secondary)
