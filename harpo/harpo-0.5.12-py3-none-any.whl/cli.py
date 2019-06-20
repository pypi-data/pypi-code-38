# Copyright 2018 Behavox Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import subprocess
import sys
import tempfile
from distutils.spawn import find_executable

import pbr.version
import yaml

from harpo import Harpo as Harpo
from harpo.users import *
from harpo.domains import HarpoDomainDoesntExist


def configure_logging(filename=None, debug=False):
    level = logging.DEBUG if debug else logging.INFO
    config = {
        'format': '[%(levelname)s] %(message)s',
        'filename': filename,
        'level': level
    }
    logging.basicConfig(**config)


def cli_parse_arguments(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='enable debug output')
    parser.add_argument('-v', '--version', action='version', version=str(pbr.version.VersionInfo('harpo')))
    parser.add_argument('--gpg-home', dest='gpg_home_sys', action='store', default='$HOME/.gnupg',
                        help='path to the user\'s GPG home')
    parser.add_argument('-D', '--base-dir', dest='basedir', action='store',
                        help='path to a directory where .harpo will be stored; required when using without git')

    main_subparsers = parser.add_subparsers(title="action", dest='action')
    main_subparsers.required = True
    main_subparsers.dest = 'action'

    # action: initialize --------------------------------------------
    initialize_parser = main_subparsers.add_parser('initialize', help='initialize harpo in a current git repo')
    initialize_parser.set_defaults(action='initialize')

    # action: add ---------------------------------------------------
    add_parser = main_subparsers.add_parser('add', help='add entity: users, domains')
    add_parser.set_defaults(action='add')
    add_subparsers = add_parser.add_subparsers(title='add user or domain', dest='target')
    add_subparsers.required = True

    # ---> target: user
    add_user = add_subparsers.add_parser('user', help='add user')
    add_user.set_defaults(target='user')

    add_user.add_argument('key', action='store', help='GPG key identifier')
    add_user.add_argument('-g', '--groups', dest='groups', action='store',
                           help='groups to add user to', default=None)

    # ---> target: group
    add_group = add_subparsers.add_parser('group', help='add group')
    add_group.set_defaults(target='group')
    add_group.add_argument('group_name', action='store', help='group to create')

    # ---> target: domain
    add_domain = add_subparsers.add_parser('domain', help='add domain')
    add_domain.set_defaults(target='domain')
    add_domain.add_argument('domain_name', action='store', help='domain to create')

    # action: remove ------------------------------------------------
    remove_parser = main_subparsers.add_parser('remove', help='remove entity: users, domains')
    remove_parser.set_defaults(action='remove')
    remove_subparsers = remove_parser.add_subparsers(title='remove user or domain', dest='target')
    remove_subparsers.required = True

    # ---> target: user
    remove_user = remove_subparsers.add_parser('user', help='remove user')
    remove_user.set_defaults(target='user')
    remove_user.add_argument('-g', '--groups', dest='groups', action='store',
                             help='groups to remove user from', default=None)

    remove_user.add_argument('key', action='store', help='GPG key identifier')

    # ---> target: group
    remove_group = remove_subparsers.add_parser('group', help='remove group')
    remove_group.set_defaults(target='group')
    remove_group.add_argument('group_name', action='store', help='group to remove')

    # ---> target: domain
    remove_domain = remove_subparsers.add_parser('domain', help='remove domain')
    remove_domain.set_defaults(target='domain')
    remove_domain.add_argument('domain_name', action='store', help='domain to remove')

    # action: list --------------------------------------------------
    list_parser = main_subparsers.add_parser('list', help='list entities: users, domains, secrets, groups')
    list_parser.set_defaults(action='list')
    list_subparsers = list_parser.add_subparsers(title='list users, domains or secrets', dest='target')
    list_subparsers.required = True

    # ---> target: user
    list_user = list_subparsers.add_parser('users', help='list users')
    list_user.set_defaults(target='users')

    # ---> target: groups
    list_groups = list_subparsers.add_parser('groups', help='list groups')
    list_groups.set_defaults(target='groups')

    # ---> target: domain
    list_domain = list_subparsers.add_parser('domains', help='list domains')
    list_domain.set_defaults(target='domains')

    # ---> target: secrets
    list_secret = list_subparsers.add_parser('secrets', help='list secrets')
    list_secret.set_defaults(target='secrets')
    list_secret.add_argument('domain_name', action='store', help='domain to list secrets from')

    # action: show --------------------------------------------------
    show_parser = main_subparsers.add_parser('show', help='show detailed information about entities')
    show_parser.set_defaults(action='show')
    show_subparsers = show_parser.add_subparsers(title='show users, groups or domains', dest='target')
    show_subparsers.required = True

    # ---> target: user
    show_user = show_subparsers.add_parser('user', help='show detailed information about users')
    show_user.set_defaults(target='user')
    show_user.add_argument('user_name', action='store', help='name of the user')

    # ---> target: groups
    show_group = show_subparsers.add_parser('group', help='show detailed information about groups')
    show_group.set_defaults(target='group')
    show_group.add_argument('group_name', action='store', help='name of the group')

    # ---> target: domain
    show_domain = show_subparsers.add_parser('domain', help='show detailed information about domains')
    show_domain.set_defaults(target='domain')
    show_domain.add_argument('domain_name', action='store', help='name of the domain')

    # action: allow -------------------------------------------------
    allow_parser = main_subparsers.add_parser('allow', help='grant users or groups access to specified domain')
    allow_parser.set_defaults(action='allow')
    allow_parser.add_argument('-u', '--user', action='store', help='list of users, comma separated')
    allow_parser.add_argument('-g', '--group', action='store', help='list of groups, comma separated')
    allow_parser.add_argument('domain_name', action='store', help='domain to grant access to')

    # action: deny --------------------------------------------------
    deny_parser = main_subparsers.add_parser('deny', help='deny users or groups access to specified domain')
    deny_parser.set_defaults(action='deny')
    deny_parser.add_argument('-u', '--user', action='store', help='list of users, comma separated')
    deny_parser.add_argument('-g', '--group', action='store', help='list of groups, comma separated')
    deny_parser.add_argument('domain_name', action='store', help='domain to revoke access to')

    # action: encrypt -----------------------------------------------
    encrypt_parser = main_subparsers.add_parser('encrypt', help='add new or update existing encrypted secret')
    encrypt_parser.set_defaults(action='encrypt')
    encrypt_parser.add_argument('secret', action='store', help='secret key in form of domain/key')
    encrypt_parser.add_argument('value', action='store', help='secret value')

    # action: encrypt-file ------------------------------------------
    encrypt_file_parser = main_subparsers.add_parser('encrypt-file', help='encrypt file')
    encrypt_file_parser.set_defaults(action='encrypt-file')
    encrypt_file_parser.add_argument('secret', action='store', help='secret key in form of domain/key')
    encrypt_file_parser.add_argument('file', action='store', help='file to encrypt')

    # action: decrypt -----------------------------------------------
    decrypt_parser = main_subparsers.add_parser('decrypt', help='decrypt and print secret')
    decrypt_parser.set_defaults(action='decrypt')
    decrypt_parser.add_argument('secret', action='store', help='secret key in form of domain/key')

    # action: reencrypt ---------------------------------------------
    reencrypt_parser = main_subparsers.add_parser('reencrypt', help='reencrypt secrets')
    reencrypt_parser.set_defaults(action='reencrypt')

    # action: edit --------------------------------------------------
    edit_parser = main_subparsers.add_parser('edit', help='edit encrypted secret')
    edit_parser.set_defaults(action='edit')
    edit_parser.add_argument('secret', action='store', help='secret key in form of domain/key')

    # action: export ------------------------------------------------
    export_parser = main_subparsers.add_parser('export', help='export domain with all its secrets and recipients')
    export_parser.set_defaults(action='export')
    export_parser.add_argument('-n', '--no-all', action='store_true', help='do not export \'all\' domain')
    export_parser.add_argument('domain', action='store', help='name of a domain to export')
    export_parser.add_argument('dest', action='store', help='destination path')

    return parser.parse_args(argv)


def print_data(data):
    print(yaml.safe_dump(data, default_flow_style=False))


def harpo_initialize(harpo):
    harpo.initialize()


def harpo_add(harpo, args):
    if args.target == 'user':
        groups = args.groups.split(',') if args.groups else []
        try:
            harpo.add_user(args.key)
        except HarpoUserExists as e:
            if groups:
                logging.info(e)
            else:
                raise
        for group in groups:
            harpo.add_user_to_group(args.key, group)
    elif args.target == 'group':
        harpo.add_group(args.group_name)
    elif args.target == 'domain':
        harpo.add_domain(args.domain_name)


def harpo_remove(harpo, args):
    if args.target == 'user':
        user = harpo.users[args.key]
        groups_to_remove = args.groups.split(',') if args.groups else [g for g in harpo.groups]
        for group in groups_to_remove:
            if harpo.groups[group].has_user(user.uid):
                harpo.remove_user_from_group(args.key, group)
        if args.groups is None:
            harpo.remove_user(args.key)
    elif args.target == 'group':
        harpo.remove_group(args.group_name)
    elif args.target == 'domain':
        harpo.remove_domain(args.domain_name)


def harpo_list(harpo, args):
    if args.target == 'users':
        print_data(harpo.list_users())
    elif args.target == 'groups':
        print_data(harpo.list_groups())
    elif args.target == 'domains':
        print_data(harpo.list_domains())
    elif args.target == 'secrets':
        print_data(harpo.domains[args.domain_name].secrets)


def harpo_show(harpo, args):
    if args.target == 'user':
        print_data(harpo.show_user(args.user_name))
    elif args.target == 'group':
        print_data(harpo.show_group(args.group_name))
    elif args.target == 'domain':
        print_data(harpo.show_domain(args.domain_name))


def harpo_allow(harpo, args):
    domain = harpo.domains[args.domain_name]
    if not domain.exists:
        raise HarpoException("Domain doesn't exist: {}".format(args.domain_name))
    if args.user:
        users = args.user.split(',')
        for user in users:
            u = harpo.users[user]
            if u.exists:
                domain.allow_user(u)
            else:
                raise HarpoUserDoesntExist(u.uid)
    if args.group:
        groups = args.group.split(',')
        for group in groups:
            g = harpo.groups[group]
            domain.allow_group(g)


def harpo_deny(harpo, args):
    domain = harpo.domains[args.domain_name]
    if not domain.exists:
        raise HarpoException("Domain doesn't exist: {}".format(args.domain_name))
    if args.user:
        users = args.user.split(',')
        for user in users:
            domain.deny_user(user)
    if args.group:
        groups = args.group.split(',')
        for group in groups:
            domain.deny_group(group)


def harpo_encrypt(harpo, args):
    domain, key = args.secret.split('/')
    harpo.encrypt(domain, key, args.value)


def harpo_encrypt_file(harpo, args):
    try:
        with open(args.file, 'r') as content_file:
            content = content_file.read()
    except OSError as e:
        logging.error(e)
        sys.exit(1)
    domain, key = args.secret.split('/')
    harpo.encrypt(domain, key, content)


def harpo_decrypt(harpo, args):
    domain, key = args.secret.split('/')
    print(harpo.decrypt(domain, key))


def harpo_reencrypt(harpo):
    harpo.reencrypt_all()


def edit_file(file):
    editor = os.environ.get('VISUAL', None) or os.environ.get('EDITOR', None)
    if editor is None:
        editor = find_executable('editor') or find_executable('vi')

    if editor is None:
        raise HarpoException("Can't find suitable editor.")
    args = [editor, file]
    logging.debug("Starting %s", args)
    subprocess.call([editor, file])


def harpo_edit(harpo, args):
    tmp = tempfile.NamedTemporaryFile(mode='w+')
    domain, key = args.secret.split('/')
    data = harpo.decrypt(domain, key)
    tmp.write(data)
    tmp.seek(0)
    edit_file(tmp.name)
    tmp.seek(0)
    content = tmp.read().strip()
    harpo.encrypt(domain, key, content)


def harpo_export(harpo, args):
    dest_harpo = Harpo(base_path=args.dest, gpg_home_sys=harpo.gpg_home)
    dest_harpo.initialize()

    domain = harpo.domains[args.domain]
    if not domain.exists:
        raise HarpoDomainDoesntExist("Domain {} doesn't exist".format(args.domain))
    dest_domain = dest_harpo.add_domain(args.domain)

    logging.info("Exporting groups...")
    for group_name in domain.recipients['groups']:
        logging.debug("Exporting %s", group_name)
        try:
            dest_harpo.add_group(group_name)
        except HarpoException as exc:
            logging.warning(exc)
        for user_name in harpo.groups[group_name].data['users']:
            try:
                dest_harpo.add_user(user_name)
            except HarpoException as exc:
                logging.warning(exc)
            dest_harpo.add_user_to_group(user_name, group_name)
        dest_domain.allow_group(dest_harpo.groups[group_name])

    logging.info("Exporting users...")
    for user_name in domain.recipients['users']:
        logging.debug("Exporting %s", user_name)
        try:
            dest_harpo.add_user(user_name)
        except HarpoException as exc:
            logging.warning(exc)
        dest_domain.allow_group(dest_harpo.users[user_name])

    logging.info("Exporting secrets...")
    for secret in domain.secrets:
        logging.debug("Export %s/%s", secret, args.domain)
        dest_harpo.encrypt(args.domain, secret, harpo.decrypt(args.domain, secret))

    if not args.no_all:
        domain_all = harpo.domains['all']
        for secret in domain_all.secrets:
            dest_harpo.encrypt('all', secret, harpo.decrypt('all', secret))
    logging.info("Done!")
    return dest_harpo


def handle_action(harpo, args):
    if args.action == 'initialize':
        harpo_initialize(harpo)

    elif args.action == 'add':
        harpo_add(harpo, args)

    elif args.action == 'remove':
        harpo_remove(harpo, args)

    elif args.action == 'list':
        harpo_list(harpo, args)

    elif args.action == 'show':
        harpo_show(harpo, args)

    elif args.action == 'allow':
        harpo_allow(harpo, args)

    elif args.action == 'deny':
        harpo_deny(harpo, args)

    elif args.action == 'encrypt':
        harpo_encrypt(harpo, args)

    elif args.action == 'encrypt-file':
        harpo_encrypt_file(harpo, args)

    elif args.action == 'decrypt':
        harpo_decrypt(harpo, args)

    elif args.action == 'reencrypt':
        harpo_reencrypt(harpo)

    elif args.action == 'edit':
        harpo_edit(harpo, args)

    elif args.action == 'export':
        harpo_export(harpo, args)


def find_harpo_basedir(cwd, name='.harpo'):
    basedir = os.path.join(cwd, name)
    if os.path.exists(basedir):
        return basedir
    else:
        if cwd == '/':
            raise RuntimeError("Unable to find .harpo and `--base-dir` isn't specified")
        new_cwd = os.path.normpath(os.path.join(cwd, '..'))
        return find_harpo_basedir(new_cwd, name)


def main(argv=None):
    args = cli_parse_arguments(argv=argv)
    configure_logging(debug=args.debug)

    if args.basedir is None:
        try:
            base_dir = find_harpo_basedir(os.getcwd())
        except RuntimeError as e:
            logging.critical(e)
            sys.exit(1)
    else:
        base_dir = args.basedir

    gpg_home_sys = os.path.expandvars(args.gpg_home_sys)
    harpo = Harpo(base_dir, gpg_home_sys=gpg_home_sys)

    try:
        handle_action(harpo, args)
        if harpo.must_be_reencrypted:
            harpo.reencrypt_all()
    except HarpoException as e:
        logging.error(e)
        sys.exit(1)
