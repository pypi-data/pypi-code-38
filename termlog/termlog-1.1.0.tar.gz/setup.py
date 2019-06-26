#!/usr/bin/env python
# isort:skip
"""
Setup.py shouldn't be updated during normal development.

Update:
   entrypoints.txt  <-- add new command-line interfaces here
   requirements.txt  <-- required for package to run
   requirements/*.txt  <-- as appropriate
"""
# ----------------------------------------------------------------------
# Version guard
# ----------------------------------------------------------------------
import sys
if sys.version_info < (3, 7):
    sys.stderr.write('Python 3.7+ is required for installation.\n')
    sys.tracebacklimit = 0
    sys.exit(1)

# ----------------------------------------------------------------------
import datetime
import itertools
import os
import re
import subprocess

# ----------------------------------------------------------------------
from pathlib import Path
from typing import List, Optional, Tuple

from setuptools import Command, setup



try:
    # pip10+
    import pip._internal.req as req
except ImportError:
    # pip9
    import pip.req as req


try:
    import pypandoc
except ImportError:
    pypandoc = None


# ----------------------------------------------------------------------
def main():
    """Run setup"""
    top_path = str(Path(__file__).parent.absolute())
    metadata = get_package_metadata(top_path=top_path)

    # Run setup
    setup(**metadata)


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------
class BuildImageCommand(Command):
    description: str = 'Builds a docker image'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from scripts.build import build_image
        build_image()


class CleanCommand(Command, object):
    description: str = 'Remove build artifacts and *.pyc'
    user_options: List = [
        ('force', 'f', 'Force clean')
        ]

    def initialize_options(self):
        self.force: bool = False

    def finalize_options(self):
        pass

    def run(self):
        self.force = True if self.force else False
        from scripts.clean import clean
        clean(force=self.force)


class CheckCommand(Command, object):
    description: str = 'Check build using twine check'
    user_options: List = [
        ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from scripts.check import check
        check()


class DistCommand(Command, object):
    description = 'Builds sdist and bdist_wheel for release'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from scripts.build import build_dist
        build_dist()


class LintCommand(Command, object):
    description = 'Runs linting and style tools'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from scripts.lint import lint
        lint()


class PrereleaseCommand(Command, object):
    description = 'Runs tests'
    user_options: List = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from scripts.build import build_dist
        from scripts.clean import clean
        from scripts.check import check
        from scripts.lint import lint
        from scripts.test import run_test
        from scripts.push import push_pypi

        clean(force=True)
        build_dist()
        lint()
        check()
        run_test(release=True, coverage_fail_threshold=75)


class ReleaseCommand(Command, object):
    description = 'Runs tests'
    user_options: List = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from scripts.build import build_dist
        from scripts.clean import clean
        from scripts.check import check
        from scripts.lint import lint
        from scripts.test import run_test
        from scripts.push import push_pypi

        clean(force=True)
        build_dist()
        lint()
        check()
        run_test(release=True, coverage_fail_threshold=75)
        push_pypi()


class TestCommand(Command, object):
    description = 'Runs tests'
    user_options: List = [
        ('release', 'r', 'Run tests as release mode'),
        ('threshold', 't', 'Threshold for coverage failure'),
        ]

    def initialize_options(self):
        self.threshold: int = 75
        self.release: bool = False

    def finalize_options(self):
        pass

    def run(self):
        from scripts.test import run_test
        run_test(release=self.release, coverage_fail_threshold=self.threshold)


class UploadCommand(Command, object):
    description = 'Push package to pypi'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from scripts.push import push_pypi
        push_pypi()


class InstallCommandCompletionCommand(Command, object):
    description = 'Install command-completions for shell'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        metadata = get_package_metadata()
        install_shell_completion(**metadata)


# ----------------------------------------------------------------------
# Support
# ----------------------------------------------------------------------
files_in_tree = set()
folders_in_tree = set()


def find_data_files(repo_path=None):
    """Captures files that are project specific.

    Args:
        repo_path (str): path to check [default: path of setup.py]

    """
    repo_path = Path(repo_path or Path(__file__).parent).absolute()

    include = ['LICENSE', 'requirements', 'requirements*.txt', 'entrypoints.txt', '*.sql', '*.sql.j2']
    found = sorted(
        str(path.absolute().relative_to(repo_path))
        for path in scan_tree(repo_path)
        if (
            any(path.match(included) for included in include)
            or any(parent.match(included) for parent in path.parents for included in include)
        ))
    return found


def find_packages(repo_path=None, top_package_name=None):
    """Finds packages; replacement for setuptools.find_packages which
    doesn't support PEP 420.

    Lengthy discussion with no resolution:
        https://github.com/pypa/setuptools/issues/97

    Assumptions:
      * Packages are folders
      * Modules are files
      * Namespaces are folders without modules
      * setup.py is for a single package
      * the folder which contains setup.py is _not_ a package itself
      * each package falls under a single tree (e.g. requests, requests.api, etc.)
      * the package is complex enough to have multiple sub folders/modules

    Args:
        repo_path (str): path to check [default: path of setup.py]

    Returns:
        list(list, list, list): Returns packages, modules and namespaces

    """
    repo_path = Path(repo_path or Path(__file__).parent).absolute()
    packages = set()
    modules = set()
    namespaces = set()
    python_artifacts = ['__pycache__']
    repo_artifacts = ['.*']
    install_artifacts = ['*.egg-info']
    build_artifacts = ['dist', 'build']
    test_files = ['tests', 'test', '.tox']
    artifacts = install_artifacts + build_artifacts + repo_artifacts + python_artifacts + test_files
    for path in scan_tree(repo_path):
        path = path.absolute().relative_to(repo_path)

        # Only include paths with .py
        if not path.match('*.py'):
            continue

        # check folders
        if any(p.match(artifact) for artifact in artifacts for p in path.parents):
            continue

        # There should be a valid package at this point
        package_name = str(path.parent).replace(os.path.sep, '.')
        module_name = str(path).replace(os.path.sep, '.').replace(path.suffix, '')
        # TODO: make this actually generic
        if not module_name.startswith(top_package_name):
            continue
        if package_name == '.':
            module_name = f'.{module_name}'
            if module_name == '.setup':
                continue
            modules.add(module_name)
            continue

        modules.add(module_name)
        packages.add(package_name)

    # find namespaces
    for module_name in modules:
        module_path = Path(module_name.replace('.', os.path.sep))
        package_name = str(module_path.parent).replace(os.path.sep, '.')
        if package_name in packages:
            continue
        namespaces.add(package_name)

    return sorted(packages), sorted(modules), sorted(namespaces)


def get_entrypoints(path=None):
    """
    """
    entry_points = {}
    path = path or 'entrypoints.txt'
    if not os.path.exists(path):
        return entry_points

    with open(path) as stream:
        for line in stream:
            if not line.strip():
                continue
            if line.strip().startswith('#'):
                continue
            entry_points.setdefault('console_scripts', []).append(line.strip())
    return entry_points


def get_license(top_path=None):
    """Reads license file and returns"""
    repo_path = top_path or os.path.realpath(os.path.dirname(__file__))
    files = {f.lower(): f for f in os.listdir(repo_path)}
    permutations = itertools.product(['license'], ['', '.txt'])
    files = [os.path.join(repo_path, f) for l, f in files.items() if l in permutations]
    license = ''
    for filepath in files:
        if os.path.exists(filepath):
            with open(filepath, 'r') as stream:
                license = stream.read()
                break
    return license


def get_package_metadata(top_path=None, package_name=None):
    """Find the __metadata__.py file and read it"""
    repo_path = str(Path(top_path or Path(__file__).parent).absolute())
    setup_cfg = Path(repo_path) / 'setup.cfg'
    if package_name is None and setup_cfg.exists():
        for line in setup_cfg.read_text('utf-8').split('\n'):
            if line.startswith("name ="):
                package_name = line.split("name = ")[-1].strip()
                break
    metadata = {}
    prefixes = ('.', '_')
    build_artifacts = ('build', 'test', 'tests')
    paths = [
        path.relative_to(repo_path)
        for path in scan_tree(repo_path)
        if path.stem == '__metadata__'
        ]
    for rel in paths:
        # Don't include the build artifacts
        if not any(parent.stem in build_artifacts for parent in rel.parents):
            # if we have a package name, lets test for it
            if package_name and not any(parent.stem == package_name for parent in rel.parents):
                continue
            d = dict(locals(), **globals())
            exec(rel.read_text('utf-8'), d, d)
            package_metadata = d.get('package_metadata')
            if package_metadata:
                metadata.update(package_metadata.setup)
                break

    requirements, dependency_links = get_package_requirements(top_path=repo_path)
    packages, modules, namespaces = find_packages(top_package_name=metadata['name'])
    # Package Properties
    long_description, long_description_content_type = get_readme()
    metadata['long_description'] = long_description
    metadata['long_description_content_type'] = long_description_content_type
    metadata.setdefault('packages', packages)
    # metadata.setdefault('include_package_data', True)

    # Requirements
    metadata.setdefault('setup_requires', requirements.get('setup') or [])
    metadata.setdefault('install_requires', requirements.get('install') or [])
    metadata.setdefault('tests_require', requirements.get('tests') or requirements.get('test') or [])
    metadata.setdefault('extras_require', requirements.get('extras') or [])
    metadata.setdefault('dependency_links', dependency_links)

    # CLI
    entry_points = get_entrypoints() or {}
    metadata.setdefault('entry_points', entry_points)

    # Packaging
    metadata.setdefault('platforms', ['any'])
    metadata.setdefault('zip_safe', False)

    year = datetime.datetime.now().year
    license = get_license() or 'Copyright {year} - all rights reserved'.format(year=year)
    metadata.setdefault('license', license)

    metadata.setdefault('classifiers', [])
    metadata['classifiers'] = list(metadata['classifiers'])

    # Extra ingestion
    metadata.setdefault('data_files', [('', find_data_files(repo_path))])

    # Add setuptools commands
    metadata.setdefault('cmdclass', get_setup_commands())

    return metadata


def get_package_requirements(top_path=None):
    """Find all of the requirements*.txt files and parse them"""
    repo_path = Path(top_path or Path(__file__).parent).absolute()
    requirements = {'extras': {}}
    dependency_links = set()
    # match on:
    #    requirements.txt
    #    requirements-<name>.txt
    #    requirements_<name>.txt
    #    requirements/<name>.txt
    options = '_-/'
    include_globs = ['requirements*.txt', 'requirements/*.txt']
    paths = [relpath for relpath in scan_tree(repo_path, include=include_globs)]
    for path in paths:
        try:
            path = path.absolute().relative_to(repo_path)
        except Exception:
            raise ValueError(f'\n\nrepo={repo_path}\npath={path}\n\n')
        if path.name == 'requirements.txt' and path.parent.name == '':
            name = 'requirements'
        elif 'requirements' in [p.name for p in path.parents]:
            name = path.name.replace(path.suffix, '')
        elif 'requirements' in path.name:
            name = path.name.replace('requirements', '').lstrip(options)
        else:
            raise Exception(f'Could not find requirements using {path}')
        reqs_, deps = parse_requirements(str(path.absolute()))
        dependency_links.update(deps)
        if name in ['requirements', 'install', '']:
            requirements['install'] = reqs_
        elif name in ['test', 'tests']:
            requirements['tests'] = reqs_
            requirements['extras']['tests'] = reqs_
        elif name in ['setup']:
            requirements['setup'] = reqs_
        else:
            requirements['extras'][name] = reqs_

    all_reqs = set()
    dev_reqs = set()
    for name, req_list in requirements.items():
        if name in ['install']:
            all_reqs.update(req_list)
        elif name in ['extras']:
            for subname, reqs in req_list.items():
                all_reqs.update(reqs)
                dev_reqs.update(reqs)
        else:
            all_reqs.update(req_list)
            dev_reqs.update(req_list)

    requirements['extras']['dev'] = list(sorted(dev_reqs))
    requirements['extras']['all'] = list(sorted(all_reqs))
    return requirements, list(sorted(dependency_links))


def get_readme(top_path: Optional[Path] = None) -> Tuple[str, str]:
    """Read the readme for the repo"""
    readme = ''
    path = Path(__file__).parent if top_path is None else top_path
    paths = {p.relative_to(path) for p in path.glob('*')}
    permutations = [
        ''.join(permutation)
        for permutation in itertools.product(['readme'], ['', '.md', '.rst', '.txt'])
        ]
    filepaths = {p for p in paths if p.name.lower() in permutations}
    content_type = 'text/x-rst'  # see: https://packaging.python.org/specifications/core-metadata/#description-content-type
    # Grabs the first one found
    for filepath in filepaths:
        readme = filepath.read_text('utf-8')
        if filepath.name.endswith('.txt'):
            content_type = 'text/plain'
        elif filepath.name.endswith('.md'):
            content_type = 'text/markdown'
        elif filepath.name.endswith('.rst'):
            content_type = 'text/x-rst'
        else:
            content_type = 'text/plain'
        break
    # See: https://github.com/pypa/setuptools/issues/1390
    readme = re.sub(pattern='\n\n+', repl='\n\n', string=readme)
    return readme, content_type


def get_setup_commands():
    """Returns setup command class list"""
    commands = {
        'build_image': BuildImageCommand,
        'check': CheckCommand,
        'cli': InstallCommandCompletionCommand,
        'clean': CleanCommand,
        'dist': DistCommand,
        'lint': LintCommand,
        'prerelease': PrereleaseCommand,
        'release': ReleaseCommand,
        'test': TestCommand,
        'upload': UploadCommand,
        }
    return commands


def install_shell_completion(**metadata):
    for cep in metadata['entry_points']['console_scripts']:
        name, _ = cep.split('=', 1)
        name = name.strip()
        cmd = f'{name} shell-completion install'
        subprocess.run(cmd, shell=True, check=False)  # some commands can't complete


def parse_requirements(path):
    template = '{name}{spec}'
    requirements = set()
    dependency_links = set()
    for requirement in req.parse_requirements(path, session="somesession"):
        if requirement.markers is not None and not requirement.markers.evaluate():
            continue

        name = requirement.name
        spec = str(requirement.req.specifier) if len(str(requirement.req.specifier)) else ''
        req_ = template.format(name=name, spec=spec)
        if req_:
            requirements.add(req_)

        link = str(requirement.link) if requirement.link else ''
        if link:
            dependency_links.add(link)

        # TODO: What do we do with these?
        if requirement.options:
            pass

    return list(sorted(requirements)), list(sorted(dependency_links))


def scan_tree(top_path=None, exclude=None, include=None):
    """Finds files in tree

    * Order is random
    * Folders which start with . and _ are excluded unless excluded is used (e.g. [])
    * This list is memoized

    Args:
        top_path (str): top of folder to search

    Yields:
        str: paths as found
    """
    repo_path = Path(top_path or Path(__file__).parent).absolute()
    if not files_in_tree:
        for root, folders, files in os.walk(repo_path):
            rel = Path(root).relative_to(repo_path)
            # Control traversal
            folders[:] = [f for f in folders if f not in ['.git']]
            folders_in_tree.update(folders)
            # Yield files
            for filename in files:
                relpath = rel.joinpath(filename)
                if relpath not in files_in_tree:
                    files_in_tree.add(relpath)
                    if include is not None:
                        if any(relpath.match(inc) for inc in include):
                            yield repo_path / relpath
                    else:
                        yield repo_path / relpath
    else:
        for relpath in files_in_tree:
            if include:
                if any(relpath.match(inc) for inc in include):
                    yield repo_path / relpath
            else:
                yield repo_path /relpath


if __name__ == '__main__':
    main()
