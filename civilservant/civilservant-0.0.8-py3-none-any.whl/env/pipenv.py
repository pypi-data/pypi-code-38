import os
import shutil
import subprocess
import sys
from pathlib import Path

import toml
from invoke.exceptions import Failure

ACTIVE = bool(os.getenv("PIPENV_ACTIVE"))
DOTENV_PATH = Path(os.getenv("PIPENV_DOTENV_LOCATION", ".env"))
PACKAGE_PREFIX = os.getenv("CS_PACKAGE_PREFIX")
PIPENV = shutil.which("pipenv") or "pipenv"
PIPFILE = Path(os.getenv("PIPENV_PIPFILE") or "Pipfile")


def get_root_path():
    """Get the pipenv root path without instantiating a Pipenv object."""
    cmd = ["pipenv", "--where"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    result.check_returncode()
    return Path(result.stdout.rstrip())


class Pipenv:
    def __init__(self, context, root_path=None, dotenv_path=DOTENV_PATH,
            package_prefix=PACKAGE_PREFIX, exit_on_error=False):
        self._context = context
        self._dotenv_path = Path(dotenv_path) if dotenv_path else None
        self._dotenv_template_path = None
        self._pipfile_lock_path = None
        self._pipfile_path = None
        self._root_path = Path(root_path) if root_path else None
        self._venv_path = None
        self.exit_on_error = exit_on_error
        self.package_prefix = package_prefix

    def _get_root_path(self):
        try:
            cmd = f"{PIPENV} --where"
            result = self._context.run(cmd, hide=True)
            return Path(result.stdout.rstrip())
        except Failure as failure:
            print(f"Unable to get pipenv root path", file=sys.stderr)
            if self.exit_on_error:
                sys.exit(failure.result.exited)
            return None

    def _get_venv_path(self):
        try:
            cmd = f"{PIPENV} --venv"
            with self._context.cd(str(self.root_path)):
                result = self._context.run(cmd, hide=True)
            return Path(result.stdout.rstrip())
        except Failure as failure:
            print(f"Unable to get pipenv venv path", file=sys.stderr)
            if self.exit_on_error:
                sys.exit(failure.result.exited)
            return None

    @property
    def active(self):
        return ACTIVE

    @property
    def dotenv_path(self):
        if not self._dotenv_path:
            self._dotenv_path = Path(self.root_path, DOTENV_PATH)
        return self._dotenv_path

    @property
    def dotenv_template_path(self):
        if not self._dotenv_template_path:
            self._dotenv_template_path = Path(self.dotenv_path.parent,
                self.dotenv_path.name + ".template")
        return self._dotenv_template_path

    def ensure_active(self):
        if not self.installed:
            if self.exit_on_error:
                print("Pipenv not installed", file=sys.stderr)
                sys.exit(1)
            return False
        if not self.active:
            if self.exit_on_error:
                print("Pipenv not active", file=sys.stderr)
                sys.exit(1)
            return False
        return True

    def get_prefixed_dev_packages(self):
        if not self.package_prefix:
            return []
        pipfile = self.load_pipfile()
        return [p for p in pipfile.get("dev-packages", {})
            if p.startswith(self.package_prefix)]
        
    def get_prefixed_packages(self, dev=True):
        if not self.package_prefix:
            return []
        pipfile = self.load_pipfile()
        regular = [p for p in pipfile.get("packages", {})
            if p.startswith(self.package_prefix)]
        if not dev:
            return sorted(regular)
        else:
            return sorted(regular + self.get_prefixed_dev_packages())
    
    def has_package(self, name):
        pipfile = self.load_pipfile()
        return name in pipfile.get("packages", {})

    def install(self, name="", version="", dev=False, editable=False, path=""):
        name_arg = name if "://" not in path else ""
        dev_arg = "--dev" if dev else ""
        editable_arg = f"-e {path}" if editable else ""
        cmd = f"{PIPENV} install {name_arg}{version} {dev_arg} {editable_arg}"
        
        try:
            with self._context.cd(str(self.root_path)):
                self._context.run(cmd, pty=True)
            return True
        except Failure as failure:
            error_arg = name_arg if name_arg else path
            print(f"Unable to install {error_arg}", file=sys.stderr)
            if self.exit_on_error:
                sys.exit(failure.result.exited)
            return False

    @property
    def installed(self):
        return bool(shutil.which("pipenv"))

    def load_pipfile(self):
        with self.pipfile_path.open() as f:
            return toml.load(f)
    
    @property
    def pipfile_lock_path(self):
        if not self._pipfile_lock_path:
            filename = self.pipfile_path.name + ".lock"
            self._pipfile_lock_path = Path(self.pipfile_path.parent, filename)
        return self._pipfile_lock_path

    @property
    def pipfile_path(self):
        if not self._pipfile_path:
            self._pipfile_path = Path(self.root_path, PIPFILE)
        return self._pipfile_path
    
    def remove(self):
        try:
            cmd = f"{PIPENV} --rm"
            with self._context.cd(str(self.root_path)):
                self._context.run(cmd, pty=True)
            return True
        except Failure as failure:
            print(f"Unable to run \"{cmd}\"", file=sys.stderr)
            if self.exit_on_error:
                sys.exit(failure.result.exited)
            return False
    
    @property
    def root_path(self):
        if not self._root_path:
            self._root_path = self._get_root_path()
        return self._root_path

    def run(self, statement, result=False, hide=False):
        try:
            cmd = f"{PIPENV} run {statement}"
            with self._context.cd(str(self.root_path)):
                result = self._context.run(cmd, pty=True, hide=hide)
            return True if not result else result
        except Failure as failure:
            print(f"Unable to run \"{cmd}\"", file=sys.stderr)
            if self.exit_on_error:
                sys.exit(failure.result.exited)
            return False if not result else failure.result
    
    @property
    def venv_path(self):
        if not self._venv_path:
            self._venv_path = self._get_venv_path()
        return self._venv_path

