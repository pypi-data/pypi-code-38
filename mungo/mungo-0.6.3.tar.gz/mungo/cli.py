import argparse
import copy
import os
import sys
from subprocess import run
from typing import Dict, Tuple, List

from yaml import safe_load

from mungo.common import vparse, plot_dependency_graph, mungoversion, QUIET
from mungo.repositorydata import RepositoryData
from mungo.solver import solve, create_dependency_graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, help="number of jobs", default=8)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument('--version', action='version', version=f'mungo {mungoversion}')
    parser.add_argument('--quiet', action='store_true')

    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='command',
                                       description='valid subcommands',
                                       help='additional help')
    subparsers.required = True

    parser_create = subparsers.add_parser('create')
    parser_create.add_argument("-n", "--name", help="the name of the environment")
    parser_create.add_argument("package_spec", nargs="*")
    parser_create.add_argument("--file", metavar="FILE", default=None)
    parser_create.add_argument("--channel", "-c", nargs=1, action="append", metavar="CHANNEL", default=[])
    parser_create.add_argument("--dag", action="store_true", default=False, help="Do not execute anything and print "
                                                                                 "the directed acyclic graph of "
                                                                                 "package dependency in the dot "
                                                                                 "language. Recommended use on Unix "
                                                                                 "systems: mungo create --dag | dot | "
                                                                                 "display")
    parser_create.add_argument("-y", "--yes", help="Do not ask for confirmation.", action="store_true")
    parser_create.add_argument("-d", "--dryrun", help="Do not apply changes, only calculate a solution.",
                               action="store_true")
    parser_create.add_argument("--offline", action="store_true")
    parser_create.add_argument("--force_download", action="store_true")

    parser_install = subparsers.add_parser('install')
    parser_install.add_argument("-n", "--name", help="the name of the environment", default=None)
    parser_install.add_argument("package_spec", nargs="+")
    parser_install.add_argument("--file", metavar="FILE", default=None)
    parser_install.add_argument("--channel", "-c", nargs=1, action="append", metavar="CHANNEL", default=[])
    parser_install.add_argument("--dag", action="store_true", default=False, help="Do not execute anything and print "
                                                                                  "the directed acyclic graph of "
                                                                                  "package dependency in the dot "
                                                                                  "language. Recommended use on Unix "
                                                                                  "systems: mungo create --dag | dot "
                                                                                  "| display")
    parser_install.add_argument("-y", "--yes", help="Do not ask for confirmation.", action="store_true")
    parser_install.add_argument("-d", "--dryrun", help="Do not apply changes, only calculate a solution.",
                                action="store_true")
    parser_install.add_argument("--offline", action="store_true")
    parser_install.add_argument("--force_download", action="store_true")

    args = parser.parse_args()
    # use either the supplied name, the current prefix or the default env 'base' in that order
    args.name = args.name or os.getenv('CONDA_DEFAULT_ENV', 'base')
    jobs = args.jobs
    command = args.command
    dag = args.dag
    ask_for_confirmation = not args.yes
    dryrun = args.dryrun
    offline = args.offline
    force_download = args.force_download
    debug = args.debug
    if args.quiet:
        QUIET.append(args.quiet)

    channels = [channel for channel in args.channel]
    channels = [l for channel in channels for l in channel if isinstance(channel, list)]  # flatten channel lists
    packages = set(args.package_spec)
    if args.file is not None:
        name, channels_rc, packages_rc, pip = _read_environment_description(args.file)
        name = name or args.name  # if the environment description does not supply a name, use args.name instead
        channels.extend(channels_rc)
        packages |= set(packages_rc)
    else:
        name = args.name
        pip = []

    default_channels = _get_condarc_channels()
    channels.extend(default_channels)

    print("WARNING: mungo is experimental, use at your own risk.", file=sys.stderr)
    execute_transaction(mode=command, name=name, channels=channels, packages=packages, pip=pip, jobs=jobs,
                        dag=dag, ask_for_confirmation=ask_for_confirmation, dryrun=dryrun, offline=offline,
                        force_download=force_download, debug=debug)


def execute_transaction(mode: str,
                        name: str,
                        channels: list,
                        packages: set,
                        pip: list,
                        jobs: int = 1,
                        dag: bool = False,
                        ask_for_confirmation: bool = False, dryrun: bool = False,
                        offline: bool = False,
                        force_download: bool = False,
                        debug: bool = False):
    local_repodata = RepositoryData.from_environment(name) if mode == "install" else None
    local_repodata_backup = copy.deepcopy(local_repodata)

    g = create_dependency_graph(channels,
                                packages,
                                [local_repodata] if local_repodata is not None else [],
                                jobs,
                                offline,
                                force_download,
                                debug)

    local_repodata = local_repodata_backup

    # print("Node count:", len(g.vs.select(type="package")))

    to_install, dep_nodes = solve(g, channels)
    if not QUIET:
        print('\n' * 7)
    installed = local_repodata.d if local_repodata is not None else None
    if dag:
        plot_dependency_graph(packages, g, to_install, dep_nodes, installed=installed)
    else:
        to_install = [n for n in to_install if not n["installed"]]
        if _install_prompt(to_install, installed, ask_for_confirmation, dryrun):
            command = "@EXPLICIT\n"
            command += '\n'.join([f'{n["data"]["channel"]}/{n["data"]["fn"]}' for n in to_install])
            cmd = f'bash -i -c "conda create --name {name} --file /dev/stdin"' if mode == "create" \
                else 'bash -i -c "conda install --file /dev/stdin"'
            ps = run(cmd, input=command.encode(), shell=True)
    return to_install


def _get_condarc_channels() -> List[str]:
    condarc_path = os.path.expanduser(os.path.join('~', '.condarc'))
    if os.path.exists(condarc_path):
        with open(os.path.expanduser(os.path.join('~', '.condarc')), 'rt') as reader:
            channels = safe_load(reader)
            return channels['channels']
    else:
        return []


def _read_environment_description(yml: str) -> Tuple[str, list, set, set]:
    with open(yml, 'rt') as reader:
        data = safe_load(reader)
        name = data.get('name', None)
        channels = data.get('channels', [])
        package_specs = {p for p in data.get('dependencies', []) if isinstance(p, str)}
        pip_specs = [p['pip'] for p in data.get('dependencies', []) if isinstance(p, dict) and 'pip' in p]
        pip_specs = {item for sublist in pip_specs for item in sublist}
        return name, channels, package_specs, pip_specs


def _install_prompt(to_install: list, installed: dict = None, ask_for_confirmation: bool = True,
                    dryrun: bool = False) -> bool:
    if len(to_install) == 0:
        if not QUIET:
            print("Nothing to do.")
        exit(0)

    def _prepare_packages(packages: dict) -> dict:
        # update package information to contain everything we need for displaying relevant information
        for package, ds in packages.items():
            for data in ds:
                if data is not None:
                    data['version_build'] = data['version'] + '-' + data['build']
                    if "channel" not in data:
                        data['reponame'] = "local"  # TODO: replace this
                    else:
                        data['reponame'] = data['channel'].split('/')[-2]
        return packages

    def _calculate_widths(packages: dict) -> Dict[str, int]:
        # calculate column-widths for the three columns 'name', 'version_build' and 'reponame'
        widths = {t: max([max([len(d_from[t]) if d_from is not None else 0, len(d_to[t])])
                          for (d_from, d_to) in packages.values()]) if len(packages) > 0 else 0
                  for t in ['name', 'version_build', 'reponame']}
        return widths

    def _print_packages(packages: dict, widths: Dict[str, int]):
        # print packages that are to be installed / updated / downgraded
        print("")
        for (package_from, package_to) in packages.values():
            if "installed" not in package_to:  # only display packages that aren't already installed
                if package_from is not None:  # if there's an update/downgrade of a package
                    print("\t{:<{name_width}} {:<{version_width}} {:<{repo_width}}  ->  "
                          "{:<{version_width}} {:<{repo_width}}"
                          .format(package_from['name'], package_from['version_build'], package_from['reponame'],
                                  package_to['version_build'], package_to['reponame'],
                                  name_width=widths['name'],
                                  version_width=widths['version_build'],
                                  repo_width=widths['reponame']))
                else:  # install a new package (not an update/downgrade of an existing package)
                    print("\t{:<{name_width}} {:<{version_width}} {:<{repo_width}}"
                          .format(package_to['name'], package_to['version_build'], package_to['reponame'],
                                  name_width=widths['name'],
                                  version_width=widths['version_build'],
                                  repo_width=widths['reponame']))
        print("")

    to_install = {node['data']['name']: node['data'] for node in to_install}

    if installed is not None:
        # which packages have changed?
        changed = installed.keys() & to_install.keys()

        # assert that there is only one version installed.
        # TODO: What do we do if there are multiple versions?
        if not all(len(installed[package].keys()) == 1 for package in installed.keys()):
            print(f"WARNING: Multiple locally installed versions for the same package.", file=sys.stderr)

        local_versions = {name: list(installed[name].values())[0] for name in changed}
        remote_versions = {name: data for name, data in to_install.items() if name in changed}
        version_changes = {package: (local_versions[package], remote_versions[package]) for package in changed}

        upgrades = {package: (p_from, p_to)
                    for (package, (p_from, p_to)) in version_changes.items()
                    if vparse(p_from['version']) < vparse(p_to['version'])
                    }
        # if vparse(([p_from['version'], p_from['build']])) < vparse(([p_to['version'], p_to['build']]))
        downgrades = {package: (p_from, p_to)
                      for (package, (p_from, p_to)) in version_changes.items()
                      # if vparse(([p_from['version'], p_from['build']])) > vparse(([p_to['version'], p_to['build']]))}
                      if vparse(p_from['version']) > vparse(p_to['version'])
                      }

        # remove packages that are to be updated or downgraded from the list of *new* packages
        for package in upgrades.keys() | downgrades.keys():
            to_install.pop(package, None)
    else:
        upgrades = dict()
        downgrades = dict()

    # add a dummy "package_from" (`None`) to get rid of special cases
    to_install = {package: (None, p_to) for (package, p_to) in to_install.items()}

    # get maximum column widths per type
    # across all three modes of package installation (install/upgrade/downgrade)
    all_widths = [_calculate_widths(_prepare_packages(packages)) for packages in [to_install, upgrades, downgrades]]
    widths = dict()
    for w in all_widths:
        for k, v in w.items():
            widths[k] = max(widths.get(k, 0), v)

    if len(upgrades) > 0:
        print("The following packages will be UPDATED:")
        _print_packages(upgrades, widths)

    if len(downgrades) > 0:
        print("The following packages will be DOWNGRADED:")
        _print_packages(downgrades, widths)

    if len(to_install) > 0:
        print("The following packages will be INSTALLED:")
        _print_packages(to_install, widths)

    if dryrun:
        print("Called as dryrun. Nothing was installed.")
        return False

    if ask_for_confirmation:
        answer = input("\nProceed ([y]/n)? ")
        if answer.lower() not in {'\n', 'y', ''}:
            return False
    return True
