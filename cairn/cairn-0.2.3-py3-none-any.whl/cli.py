import argparse
import subprocess
import sys
import re

from cairn.versions import next_version, validate_mode, VersionMatchError


def _mode(text):
    validate_mode(text)
    return text


def _name(text):
    if ' ' in text:
        raise RuntimeError('Name must not have spaces in it')
    return text


def current_version():
    cmd = [
        'git', 'describe', '--always'
    ]
    output = subprocess.check_output(cmd).decode().strip()
    return output


def create_tag(name, dry_run):
    # create the git tag
    if not dry_run:
        cmd = [
            'git',
            'tag',
            '-a', name,
            '-m', name,
        ]
        subprocess.check_call(cmd)

    else:
        print('Next Version:', name)


def current_branch():
    cmd = ['git', 'branch']
    output = subprocess.check_output(cmd).decode()

    branch_name = None
    for line in output.splitlines():
        items = tuple(filter(lambda x: len(x), line.split(' ')))
        if len(items) == 2 and items[0] == '*':
            branch_name = items[1]
            break
    assert branch_name is not None
    return branch_name


def parse_commandline():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # common args
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Do not perform tagging simply print new tag')

    # update parser
    parser_update = subparsers.add_parser('update', aliases=('up',))
    parser_update.add_argument('mode', type=_mode, default='patch', nargs='?', help='The type of version increment')
    parser_update.add_argument('-E', '--empty-commit', action='store_true', help='Create tag on new empty commit')
    parser_update.set_defaults(handler=run_update)

    # create parser
    parser_create = subparsers.add_parser('create', aliases=('new',))
    parser_create.add_argument('name', type=_name, default='v0.0.1', nargs='?', help='The name of the new tag')
    parser_create.add_argument('-E', '--empty-commit', action='store_true', help='Create tag on new empty commit')
    parser_create.set_defaults(handler=run_create)

    # release parser
    parser_release = subparsers.add_parser('release')
    parser_release.add_argument('-f', '--final', action='store_true', help='Mark this as the final re')
    parser_release.set_defaults(handler=run_release)

    return parser, parser.parse_args()


def run_update(args):
    # extract the current version of the project
    curr_ver = current_version()

    # generate the next version of the project
    next_ver = next_version(curr_ver, args.mode)

    if args.dry_run:
        print('Next version: {}'.format(next_ver))
        return False

    if next_ver is None:
        print('Unable to generate a new ')

    if args.empty_commit:
        cmd = ['git', 'commit', '--allow-empty', '-m', 'Update version to {}'.format(next_ver)]
        subprocess.check_call(cmd)

    create_tag(next_ver, args.dry_run)

    return True


def run_create(args):

    if args.empty_commit:
        cmd = ['git', 'commit', '--allow-empty', '-m', 'Update version to {}'.format(args.name)]
        subprocess.check_call(cmd)

    create_tag(args.name, args.dry_run)

    return True


def run_release(args):
    release_point_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()

    active_branch = current_branch()
    current = current_version()
    release_version = next_version(current, 'patch')
    release_branch = 'release/' + release_version[:-1] + 'x'
    following_version = next_version(release_version, 'minor-iota')

    description = 'release'
    if not args.final:
        release_version += '-rc1'
        description += ' candidate'

    print('--------------------------------------------------------------------------')
    print('    Active Branch:', active_branch)
    print('   Release Branch:', release_branch)
    print('  Current Version:', current)
    print('  Release Version:', release_version)
    print('Following Version:', following_version)
    print('    Release Point:', release_point_sha)
    print('--------------------------------------------------------------------------')
    print()

    if args.dry_run:
        return False

    # create the new branch
    cmd = ['git', 'checkout', '-b', release_branch]
    subprocess.check_call(cmd)

    # create the empty commit
    cmd = ['git', 'commit', '--allow-empty', '-m', 'Create initial {} ({})'.format(description, release_version)]
    subprocess.check_call(cmd)

    # tag the release version
    create_tag(release_version, args.dry_run)

    # checkout the active branch again
    cmd = ['git', 'checkout', active_branch]
    subprocess.check_call(cmd)

    # create the empty commit
    cmd = ['git', 'commit', '--allow-empty', '-m', 'Update version to {}'.format(following_version)]
    subprocess.check_call(cmd)

    # tag the release version
    create_tag(following_version, args.dry_run)

    return True


def main():
    parser, args = parse_commandline()

    if not hasattr(args, 'handler'):
        parser.print_usage()
        sys.exit(1)

    success = False
    try:
        success = args.handler(args)
    except VersionMatchError as ex:
        print('Current version: {} can not be matched. Sorry!'.format(ex.version))

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
