import os
from pathlib import Path
from urllib.parse import urlsplit

PACKAGE_DIR_PREFIX = os.environ["CS_PACKAGE_DIR_PREFIX"]
PACKAGE_PREFIX = os.environ["CS_PACKAGE_PREFIX"]
PACKAGE_URL_PREFIX = os.environ["CS_PACKAGE_URL_PREFIX"]
PROJECT_LIBS_PATH = os.environ["CS_PROJECT_LIBS_PATH"]


def build_git_url(arg, pkg):
    """Construct a git URL from a package name."""
    maybe_url = urlsplit(arg)
    if maybe_url.scheme:
        if not maybe_url.scheme.startswith("git"):
            arg = "git+" + arg
        if maybe_url.fragment != f"egg={pkg}":
            arg += f"#egg={pkg}"
        return arg
    pkg_dir = pkg.replace(PACKAGE_PREFIX, PACKAGE_DIR_PREFIX)
    return f"{PACKAGE_URL_PREFIX}{pkg_dir}#egg={pkg}"


def check_installed(pipenv, pkg):
    """Check whether a particular package has been installed."""
    result = pipenv.run("pip list --format=freeze", result=True, hide=True)
    installed = set(line.split("==")[0] for line in result.stdout.split("\n"))
    return pkg in installed


def extract_package_name(arg):
    """Extract the package name from a URL or other name variant."""
    maybe_url = urlsplit(arg)
    if maybe_url.scheme:
        # pipenv requires an #egg fragment for version-controlled dependencies
        if not maybe_url.fragment.startswith("egg="):
            return None
        return maybe_url.fragment[4:]
    if arg.startswith(PACKAGE_DIR_PREFIX):
        return arg.replace(PACKAGE_DIR_PREFIX, PACKAGE_PREFIX)
    if not arg.startswith(PACKAGE_PREFIX):
        return PACKAGE_PREFIX + arg
    return arg


def link_package(pipenv, pkg):
    """Symlink an installed package into the project's libs directory."""
    project_libs_path = Path(pipenv.root_path, PROJECT_LIBS_PATH)
    project_libs_path.mkdir(parents=True, exist_ok=True)
    local_pkg_path = Path(project_libs_path, pkg)
    if local_pkg_path.exists():
        local_pkg_path.unlink()
    venv_pkg_path = Path(pipenv.venv_path, "src", pkg)
    local_pkg_path.symlink_to(venv_pkg_path, target_is_directory=True)

