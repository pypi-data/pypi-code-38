import importlib.util
import os
import sys
from pathlib import Path

from invoke import task

from ..pipenv import Pipenv
from ..utils.dotenv import concat_dotenv_templates
from ..utils.package import (build_git_url, check_installed,
    extract_package_name, link_package)
from ..utils.print import print_action, print_error, print_warning

CORE_LIB_URL = os.environ["CS_CORE_LIB_URL"]
PROJECT_LIBS_PATH = Path(os.environ["CS_PROJECT_LIBS_PATH"])
TEST_ENV = ".env.test"

def _include_library(pipenv, arg, title=True):
    """Include an individual CivilServant library in the application."""
    if title:
        print_action("Including ", arg)
    pkg = extract_package_name(arg)
    if not pkg:
        print_error(f"Fragment #egg=name missing from {arg}")
        sys.exit(1)
    url = build_git_url(arg, pkg)
    if not pipenv.has_package(pkg):
        pipenv.install(editable=True, path=url)
    link_package(pipenv, pkg)


@task
def check(c):
    """Check whether the project is initialized and in a consistent state."""
    print_action("Ensuring the project is in a consistent state""")
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()

    packages = pipenv.get_prefixed_packages(dev=True)
    missing = [pkg for pkg in packages if not check_installed(pipenv, pkg)]
    for package in missing:
        print_error("CivilServant library in Pipfile not installed: ", package)

    libs_path = Path(pipenv.root_path, PROJECT_LIBS_PATH)
    if not libs_path.exists():
        print_error("Directory not found: ", str(libs_path))
    else:
        libs = set(path.name for path in libs_path.iterdir())
        for package in packages:
            if package not in libs:
                print_error("Library symlink not found: ", package)

    if not pipenv.dotenv_template_path.exists():
        print_warning("File not found: ", pipenv.dotenv_template_path.name)
    if not pipenv.dotenv_path.exists():
        print_warning("File not found: ", pipenv.dotenv_path.name)
    if not check_installed(pipenv, "pytest"):
        print_error("Test package not installed: ", "pytest")


@task
def clean(c, force=False, preserve_libs=False, preserve_lock_file=False):
    """Runs "pipenv --rm" and removes Pipfile.lock and the lib directory."""
    
    # TODO This should check for uncommited git changes in the included
    # libraries since they will be lost after running pipenv --rm. Otherwise
    # the preserve_lib flag is somewhat useless since it will preserve the
    # library symlinks but delete their targets.

    if not force:
        msg = "Pass in --force so I know you're doing this on purpose"
        print_warning(msg)
        sys.exit(1)
    else:
        print_action("Cleaning out the CivilServant installation")

    pipenv = Pipenv(c)
    pipenv.ensure_active()
    
    if not preserve_libs and PROJECT_LIBS_PATH.exists():
        print_action("Removing the included CivilServant libraries")
        for path in PROJECT_LIBS_PATH.iterdir():
            try:
                path.unlink()
            except:
                print_warning("Unable to remove the library ", path.name)
        try:
            PROJECT_LIBS_PATH.rmdir()
        except:
            msg = "Unable to remove the CivilServant libraries directory at "
            print_warning(msg, PROJECT_LIBS_PATH)
            
    if not preserve_lock_file:
        print_action("Removing the lock file")
        pipenv.pipfile_lock_path.unlink()

    print_action("Removing the pipenv environment")
    if not pipenv.remove():
        print_error("Unable to remove the pipenv environment")


@task
def env(c, write_file=False):
    """Concatenate the template env files in each CivilServant library."""
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()
    
    envs = concat_dotenv_templates(pipenv)
    if not envs:
        print_error("Project not initialized. Please run \"cs init\" first")
        return
    if write_file:
        with pipenv.dotenv_template_path.open("w") as f:
            f.writelines(envs)
    else:
        for line in envs:
            print(line, end="")


@task
def include(c, lib=[]):
    """Include one or more CivilServant libraries into the application."""
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()

    if not lib:
        print_error("No libraries specified")
        sys.exit(1)

    print_action("Including requested CivilServant libraries")
    for arg in lib:
        _include_library(pipenv, arg)


@task
def init(c, lib=[]):
    """Initialize a new CivilServant application project."""
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()
    
    prefixed_packages = pipenv.get_prefixed_packages()
    if prefixed_packages:
        print_action("Including CivilServant libraries from the Pipfile")
        for pkg in prefixed_packages:
            print_action("Including Pipfile package ", pkg)
            _include_library(pipenv, pkg, title=False)
    
    if not pipenv.has_package("civilservant-core"):
        print_action("Including required CivilServant libraries")
        _include_library(pipenv, CORE_LIB_URL)
    
    Path(pipenv.root_path, PROJECT_LIBS_PATH).mkdir(exist_ok=True)
    if lib:
        include(c, lib)

    if not pipenv.dotenv_path.exists():
        print_action("Compiling and writing the .env.template file")
        env(c, write_file=True)


@task
def test(c, env=None, x=False):
    """Run project tests in the test environment."""
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()
    
    test_env_path = Path(env) if env else Path(pipenv.root_path, TEST_ENV)
    test_pipenv = Pipenv(c, dotenv_path=test_env_path, exit_on_error=True)
    test_pipenv.run(f"pytest {'-x' if x else ''}")

