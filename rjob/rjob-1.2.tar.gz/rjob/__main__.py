#!/usr/bin/env python3
import argparse
import asyncio
import getpass
import json
import logging
import os
import sys

from .project import Project


async def initialize(args):
    name = os.path.basename(os.getcwd())
    user = getpass.getuser()

    project = Project(
        name=name,
        command="echo hello world",
        servers=(user + '@localhost',),
    )
    content = json.dumps(project.to_dict(), indent=4)
    with open('deploy.json', 'wt') as f:
        f.write(content)

    with open('.jobignore', 'wt') as f:
        f.write("""venv
.idea
.jobignore
complete
""")
    print(content)


async def deploy(args):
    project = Project.load(debug=args.debug)
    await project.deploy()


async def patch(args):
    project = Project.load(debug=args.debug)
    await project.patch()


async def start(args):
    project = Project.load(debug=args.debug)
    await project.start()


async def stop(args):
    project = Project.load(debug=args.debug)
    await project.stop()


async def wait(args):
    project = Project.load(debug=args.debug)
    await project.wait()


async def gather(args):
    project = Project.load(debug=args.debug)
    await project.collect()


async def status(args):
    project = Project.load(debug=args.debug)
    statuses = await project.statuses()
    for (deployment, status) in statuses:
        print(status.ljust(10, ' '), deployment.server)


def main():
    parser = argparse.ArgumentParser(description='dummy remote task executor')
    parser.add_argument('--debug', dest='debug', action='store_true', help="show commands during execution")
    parser.set_defaults(debug=False)

    commands = parser.add_subparsers()

    init_cmd = commands.add_parser('init', help='initialize new project in the directory')
    init_cmd.set_defaults(func=initialize)

    deploy_cmd = commands.add_parser('deploy', help='deploy project to servers but not start')
    deploy_cmd.set_defaults(func=deploy)

    patch_cmd = commands.add_parser('patch', help='patch (diff only) project to servers but not start')
    patch_cmd.set_defaults(func=patch)

    start_cmd = commands.add_parser('start', help='start processes on all servers')
    start_cmd.set_defaults(func=start)

    stop_cmd = commands.add_parser('stop', help='stop processes on all servers')
    stop_cmd.set_defaults(func=stop)

    wait_cmd = commands.add_parser('wait', help='wait when all processes will be completed')
    wait_cmd.set_defaults(func=wait)

    gather_cmd = commands.add_parser('gather', help='gather "done" directories from all servers to local host')
    gather_cmd.set_defaults(func=gather)

    status_cmd = commands.add_parser('status', help='collect job status from all servers')
    status_cmd.set_defaults(func=status)

    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(level=logging.INFO)
    if hasattr(args, 'func'):
        task = args.func(args)
        asyncio.get_event_loop().run_until_complete(task)


if __name__ == '__main__':
    main()
