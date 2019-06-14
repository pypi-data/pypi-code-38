import shlex
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
)

# Hack to avoid circular imports for mypy
if TYPE_CHECKING:
    from .whiteprint import Whiteprint


class Prefab:
    """
    Declarative deployment specifications.

    Requirements:
    - Implement execute() & validate() for default modes:
        install, update, clean, start, stop
    - Idempotent (failures can always be retried)
    """
    def execute(self, whiteprint: 'Whiteprint', mode: str) -> None:
        raise NotImplementedError

    def validate(self, whiteprint: 'Whiteprint', mode: str) -> Optional[str]:
        raise NotImplementedError


class Apt(Prefab):
    def __init__(self, packages: List[str]):
        # TODO: Support packages with version specification.
        assert isinstance(packages, list)
        assert len(packages) > 0
        self.packages = [pkg.lower() for pkg in packages]

    def execute(self, whiteprint: 'Whiteprint', mode: str) -> None:
        if mode == 'install':
            whiteprint.exec('apt install -y %s' % ' '.join(self.packages))

    def validate(self, whiteprint: 'Whiteprint', mode: str) -> Optional[str]:
        if mode == 'install':
            res = whiteprint.exec(
                'apt -qq list %s' % ' '.join(self.packages))
            installed_packages = set()
            for line in res.stdout.decode('utf-8').splitlines():
                installed_package, _ = line.split('/', 1)
                installed_packages.add(installed_package.lower())
            for package in self.packages:
                if package not in installed_packages:
                    return 'Apt package %r missing.' % package
            return None
        else:
            return None


class Pip3(Prefab):
    def __init__(self, packages: List[str]):
        # TODO: Support packages with version specification.
        self.packages = [pkg.lower() for pkg in packages]

    def execute(self, whiteprint: 'Whiteprint', mode: str) -> None:
        if mode == 'install':
            whiteprint.exec('pip3 install %s' % ' '.join(self.packages))

    def validate(self, whiteprint: 'Whiteprint', mode: str) -> Optional[str]:
        if mode == 'install':
            res = whiteprint.exec(
                'pip3 show %s' % ' '.join(self.packages))
            installed_packages = set()
            for line in res.stdout.decode('utf-8').splitlines():
                if line.startswith('Name: '):
                    installed_package = line.split(maxsplit=1)[1]
                    installed_packages.add(installed_package.lower())
            for package in self.packages:
                if package not in installed_packages:
                    return 'Pip3 package %r missing.' % package
            return None
        else:
            return None


class FolderExists(Prefab):
    def __init__(self, path: str, owner: Optional[str] = None,
                 group: Optional[str] = None, mode: Optional[int] = None,
                 remove_on_clean: bool = True):
        self.path = path
        self.owner = owner
        self.group = group
        self.mode = mode
        self.remove_on_clean = remove_on_clean

    def execute(self, whiteprint: 'Whiteprint', mode: str) -> None:
        quoted_path = shlex.quote(self.path)
        if mode == 'install':
            cmd = 'mkdir -p '
            if self.mode is not None:
                cmd += ' -m {:o} '.format(self.mode)
            cmd += self.path
            whiteprint.exec(cmd)
            if self.owner is not None:
                whiteprint.exec('chown {} {}'.format(self.owner, quoted_path))
            if self.group is not None:
                whiteprint.exec('chgrp {} {}'.format(self.group, quoted_path))
            if self.mode is not None:
                whiteprint.exec('chmod {:o} {}'.format(self.mode, quoted_path))
        elif mode == 'clean':
            if self.remove_on_clean:
                whiteprint.exec('rm -rf {}'.format(quoted_path))

    def validate(self, whiteprint: 'Whiteprint', mode: str) -> Optional[str]:
        quoted_path = shlex.quote(self.path)
        if mode == 'install':
            res = whiteprint.exec(
                'stat -c "%F %U %G %a" {!r}'.format(quoted_path), error_ok=True)
            if res.exit_status == 1:
                return '%r does not exist.' % quoted_path
            # Use rsplit because %F can return "directory" or a multi-word like
            # "regular empty file"
            file_type, owner, group, file_mode_raw = res.stdout\
                .decode('utf-8').strip().rsplit(maxsplit=3)
            file_mode = int(file_mode_raw, base=8)
            if file_type != 'directory':
                return '%r is not a directory.' % quoted_path
            elif self.owner is not None and owner != self.owner:
                return 'expected %r to have owner %r, got %r' % (
                    quoted_path, self.owner, owner)
            elif self.group is not None and group != self.group:
                return 'expected %r to have group %r, got %r' % (
                    quoted_path, self.group, group)
            elif self.mode is not None and file_mode != self.mode:
                return 'expected {!r} to have mode {:o}, got {:o}.'.format(
                    quoted_path, self.mode, file_mode)
            else:
                return None
        elif mode == 'clean':
            res = whiteprint.exec(
                'stat {!r}'.format(quoted_path), error_ok=True)
            if res.exit_status != 1:
                return 'expected %r to not exist.' % quoted_path
            else:
                return None
        else:
            return None


class LineInFile(Prefab):
    def __init__(self, path: str, line: str):
        self.path = path
        assert '\n' not in line
        assert '\r' not in line
        self.line = line

    def execute(self, whiteprint: 'Whiteprint', mode: str) -> None:
        quoted_line = shlex.quote(self.line)
        if mode == 'install':
            res = whiteprint.exec(
                'grep -q {} {}'.format(quoted_line, self.path), error_ok=True)
            if res.exit_status == 0:
                return None
            elif res.exit_status == 1 or res.exit_status == 2:
                # 1: Line not found in file
                # 2: File does not exist
                whiteprint.exec(
                    'echo {} >> {}'.format(quoted_line, self.path))
            else:
                assert False, 'Unknown grep exit status: %d' % res.exit_status
        elif mode == 'clean':
            quoted_pattern = shlex.quote('/^{}$/d'.format(self.line))
            whiteprint.exec(
                'sed --in-place="" {} {}'.format(quoted_pattern, self.path))

    def validate(self, whiteprint: 'Whiteprint', mode: str) -> Optional[str]:
        quoted_line = shlex.quote(self.line)
        if mode == 'install':
            res = whiteprint.exec(
                'grep -q {} {}'.format(quoted_line, self.path), error_ok=True)
            if res.exit_status == 0:
                return None
            else:
                return 'Line {!r}{} not found in {!r}'.format(
                    quoted_line[:10], '' if len(quoted_line) < 10 else '...',
                    self.path)
        elif mode == 'clean':
            res = whiteprint.exec(
                'grep -q {} {}'.format(quoted_line, self.path), error_ok=True)
            if res.exit_status == 1 or res.exit_status == 2:
                return None
            elif res.exit_status == 0:
                return 'Found line {!r}{} in {!r}'.format(
                    quoted_line[:10], '' if len(quoted_line) < 10 else '...',
                    self.path)
            else:
                return 'Unknown exit status from grep: {}'.format(
                    res.exit_status)
        else:
            return None
