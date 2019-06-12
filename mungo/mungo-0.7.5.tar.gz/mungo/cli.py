import json
import sys
from sys import stderr

import argparse
import copy
import logging
import os
import tempfile
from subprocess import run

from joblib import parallel_backend
from tqdm import tqdm
from typing import Dict, Tuple, List
from yaml import safe_load

import mungo
from mungo.common import vparse, plot_dependency_graph, QUIET, TqdmStream
from mungo.repositorydata import RepositoryData
from mungo.solver import solve, create_dependency_graph

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, help="number of jobs", default=8)
    parser.add_argument("-v", "--verbose", action="count", default=1)
    parser.add_argument('--version', action='version', version=f'mungo {mungo.__version__}')
    parser.add_argument('--quiet', action='store_true')

    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='command',
                                       description='valid subcommands',
                                       help='additional help')
    subparsers.required = True

    parser_create = subparsers.add_parser('create')
    parser_create.add_argument("package_spec", nargs="*")

    parser_install = subparsers.add_parser('install')
    parser_install.add_argument("package_spec", nargs="+")

    subparsers = [parser_create, parser_install]
    for subparser in subparsers:
        subparser.add_argument("-n", "--name", help="the name of the environment")

        subparser.add_argument("--file", metavar="FILE", default=None)
        subparser.add_argument("--channel", "-c", nargs=1, action="append", metavar="CHANNEL", default=[])
        subparser.add_argument("--dag", action="store_true", default=False, help="Do not execute anything and print "
                                                                                 "the directed acyclic graph of "
                                                                                 "package dependency in the dot "
                                                                                 "language. Recommended use on Unix "
                                                                                 "systems: mungo create --dag | dot | "
                                                                                 "display")
        group = subparser.add_mutually_exclusive_group()
        group.add_argument("-y", "--yes", help="Do not ask for confirmation.", action="store_true")
        group.add_argument("-d", "--dryrun", help="Do not apply changes, only calculate a solution.", action="store_true")
        subparser.add_argument("--offline", action="store_true")
        subparser.add_argument("--force_download", action="store_true")
        subparser.add_argument("--porcelain", action="store_true", help="Write output as json. Requires either --yes or --dryrun.")

    args = parser.parse_args()
    if args.porcelain and (not args.dryrun and not args.yes):
        parser.error("--porcelain requires --dryrun or --yes.")

    args.verbose = 70 - (10 * args.verbose) if args.verbose > 0 else 0
    if args.quiet:
        args.verbose = 60
    logging.basicConfig(format='%(levelname)s: %(message)s', level=args.verbose, stream=TqdmStream)

    # use either the supplied name, the current prefix or the default env 'base' in that order
    args.name = args.name or os.getenv('CONDA_DEFAULT_ENV', 'base')
    jobs = args.jobs
    command = args.command
    dag = args.dag
    ask_for_confirmation = not args.yes
    dryrun = args.dryrun
    offline = args.offline
    force_download = args.force_download
    porcelain = args.porcelain
    if args.quiet or porcelain:
        # TODO: if args.json, redirect logging to different stream / use different logging handlers
        QUIET.append(True)

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

    print("WARNING: mungo is experimental, use at your own risk.\n", file=stderr)

    execute_transaction(mode=command, name=name, channels=channels, packages=packages, pip=pip, jobs=jobs,
                        dag=dag, ask_for_confirmation=ask_for_confirmation, dryrun=dryrun, offline=offline,
                        force_download=force_download, json=porcelain)


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
                        json: bool = False):
    local_repodata = RepositoryData.from_environment(name) if mode == "install" else None
    if local_repodata:
        packages.update(local_repodata.packages)
    if "python" in packages:
        packages.remove("python")  # TODO

    local_repodata_backup = copy.deepcopy(local_repodata)

    g = create_dependency_graph(channels,
                                packages,
                                [local_repodata] if local_repodata is not None else [],
                                jobs,
                                offline,
                                force_download)

    local_repodata = local_repodata_backup

    log.debug(f"Node count {len(g.vs.select(type='package'))}")

    to_install, dep_nodes = solve(g, channels, jobs=jobs)
    installed = local_repodata.d if local_repodata is not None else None
    if dag:
        plot_dependency_graph(packages, g, to_install, dep_nodes, installed=installed)
    else:
        if _install_prompt(to_install, installed, ask_for_confirmation=ask_for_confirmation, dryrun=dryrun, porcelain=json):
            pkglist = b"@EXPLICIT\n"
            pkglist += b'\n'.join([f'{n["data"]["channel"]}/{n["data"]["fn"]}'.encode() for n in to_install])
            log.debug(f"Package file for installation via conda --file:\n{pkglist.decode()}")
            with tempfile.NamedTemporaryFile() as fp:
                fp.write(pkglist)
                fp.flush()
                cmd = f'bash -i -c "conda {mode} --name {name} --file {fp.name}"'
                log.debug(f"Calling `{cmd}`.")
                ps = run(cmd, shell=True)
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
                    dryrun: bool = False, porcelain: bool = False) -> bool:
    if len(to_install) == 0:
        if not QUIET:
            tqdm.write("Nothing to do.")
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
        tqdm.write("")
        for (package_from, package_to) in packages.values():
            if package_from is not None:  # if there's an update/downgrade of a package
                tqdm.write("\t{:<{name_width}} {:<{version_width}} {:<{repo_width}}  ->  "
                           "{:<{version_width}} {:<{repo_width}}"
                           .format(package_from['name'], package_from['version_build'], package_from['reponame'],
                                   package_to['version_build'], package_to['reponame'],
                                   name_width=widths['name'],
                                   version_width=widths['version_build'],
                                   repo_width=widths['reponame']))
            else:  # install a new package (not an update/downgrade of an existing package)
                tqdm.write("\t{:<{name_width}} {:<{version_width}} {:<{repo_width}}"
                           .format(package_to['name'], package_to['version_build'], package_to['reponame'],
                                   name_width=widths['name'],
                                   version_width=widths['version_build'],
                                   repo_width=widths['reponame']))
        tqdm.write("")

    reinstall = {node['data']['name']: node['data'] for node in to_install if node['reinstall']}
    to_install = {node['data']['name']: node['data'] for node in to_install}

    if installed is not None:
        # which packages have changed?
        changed = installed.keys() & to_install.keys()

        # assert that there is only one version installed.
        # TODO: What do we do if there are multiple versions?
        if not all(len(installed[package].keys()) == 1 for package in installed.keys()):
            log.warning(f"Multiple locally installed versions for the same package:")
            for pkg in (package for package in installed.keys() if len(installed[package].keys()) > 1):
                log.warning(f"\t{pkg}")
        local_versions = {name: list(installed[name].values())[0] for name in changed}
        remote_versions = {name: data for name, data in to_install.items() if name in changed}
        version_changes = {package: (local_versions[package], remote_versions[package]) for package in changed}
        version_changes.update(
            {package: (data, data) for package, data in to_install.items() if package in reinstall.keys()})

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

        reinstalls = {package: (p_from, p_to)
                      for (package, (p_from, p_to)) in version_changes.items()
                      # if vparse(([p_from['version'], p_from['build']])) > vparse(([p_to['version'], p_to['build']]))}
                      if vparse(p_from['version']) == vparse(p_to['version'])
                      }

        # remove packages that are to be updated or downgraded from the list of *new* packages
        for package in upgrades.keys() | downgrades.keys() | reinstalls.keys():
            to_install.pop(package, None)
    else:
        upgrades = dict()
        downgrades = dict()
        reinstalls = dict()

    # add a dummy "package_from" (`None`) to get rid of special cases
    to_install = {package: (None, p_to) for (package, p_to) in to_install.items()}

    # get maximum column widths per type
    # across all three modes of package installation (install/upgrade/downgrade)
    all_widths = [_calculate_widths(_prepare_packages(packages)) for packages in
                  [to_install, upgrades, downgrades, reinstalls]]
    widths = dict()
    for w in all_widths:
        for k, v in w.items():
            widths[k] = max(widths.get(k, 0), v)

    if porcelain:
        link = []
        for c in [upgrades, downgrades, reinstalls, to_install]:
            for n, (_, package_to) in c.items():
                link.append(package_to)
        json.dump(dict(FETCH=link), sys.stdout, indent=2)
        print()
    else:
        if len(upgrades) > 0:
            tqdm.write("The following packages will be UPDATED:")
            _print_packages(upgrades, widths)

        if len(downgrades) > 0:
            tqdm.write("The following packages will be DOWNGRADED:")
            _print_packages(downgrades, widths)

        if len(reinstalls) > 0:
            tqdm.write("The following packages will be REINSTALLED:")
            _print_packages(reinstalls, widths)

        if len(to_install) > 0:
            tqdm.write("The following packages will be INSTALLED:")
            _print_packages(to_install, widths)

    if dryrun:
        if not QUIET:
            tqdm.write("Called as dryrun. Nothing was installed.")
        return False

    if ask_for_confirmation:
        answer = input("\nProceed ([y]/n)? ")
        if answer.lower() not in {'\n', 'y', ''}:
            return False
    return True
