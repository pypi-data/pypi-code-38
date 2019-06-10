import contextlib
import os
import shutil
import stat
from unittest.mock import MagicMock

import git
import yaml


class MockVersionControlSystem:
    index = MagicMock()

    def is_dirty(self):
        return False


class CodeRepository:
    """Encapsulates file-writes and version control functionalities."""

    def __init__(self, workdir, vcs=None):
        self.workdir = workdir
        try:
            self.vcs = vcs or git.Repo(self.workdir)
        except git.exc.InvalidGitRepositoryError:
            self.vcs = MockVersionControlSystem()
        self.dirty = False

    def abspath(self, dst=None):
        """Return the absolute path of `dst`."""
        return os.path.join(self.workdir, dst)\
            if dst is not None else\
            self.workdir

    def join(self, *args):
        return os.path.join(self.workdir, *args)

    def remove(self, path):
        """Remove `path` from the repository."""
        src = self.abspath(path)
        if os.path.isfile(src):
            self.vcs.index.remove([src])
            os.unlink(src)
        elif os.path.isdir(src):
            [self.remove(os.path.join(path, x)) for x in os.listdir(src)]
            shutil.rmtree(src)
        else:
            raise NotImplementedError("Not a file or directory: %s" % src)

    def listdir(self, path):
        """Invoke :func:`os.listdir()` on the specified `path`."""
        return os.listdir(self.abspath(path))

    def mkdir(self, path):
        """Create a directory in the repository."""
        dst = self.abspath(path)
        os.makedirs(dst, exist_ok=True)
        return dst

    def exists(self, path):
        """Return a boolean indicating if `path` exists."""
        return os.path.exists(os.path.join(self.workdir, path))

    def touch(self, path):
        """Ensure that a path exists."""
        dst = self.abspath(path)
        if os.system(f'touch {dst}') != 0:
            raise Exception
        self.vcs.index.add([dst])
        self.dirty = True

    @contextlib.contextmanager
    def commit(self, msg, noprefix=False):
        """Return a context guard that commits the codebase after it exits."""
        try:
            yield self
        except Exception:
            raise
        if self.vcs.is_dirty() and self.dirty:
            self.vcs.index.commit(msg if noprefix else f'qsa: {msg}')
        self.dirty = False

    @contextlib.contextmanager
    def open(self, path, mode='w'):
        src = self.abspath(path)
        yield open(src, mode)
        self.vcs.index.add([src])
        self.dirty = True

    def read(self, path, mode='r'):
      """Read the contents of `path`."""
      return open(self.abspath(path), mode).read()

    def write(self, dst, content, mode='w', overwrite=True, newline=True):
        """Writes `content` to `dst`.

        Args:
            dst (str): destination to write content to.
            content (str,bytes): the file content.
            mode (str): mode to open the file as (``w`` or ``wb``).

        Returns:
            None
        """
        if self.exists(dst) and not overwrite:
            return
        if newline and content and not content.endswith('\n'):
            content += '\n'

        dst = self.abspath(dst)
        assert mode in ('w','wb', 'a')
        assert isinstance(content, (str, bytes))
        with open(dst, mode) as f:
            f.write(content)
        self.vcs.index.add([dst])
        self.dirty = True

    def make_executable(self, path):
        src = self.abspath(path)
        os.chmod(src, os.stat(src).st_mode | stat.S_IEXEC)
        self.vcs.index.add([src])
        self.dirty = True

    def render(self, template_name, dst, ctx=None, env=None, overwrite=True):
        """Render template `template_name` to `dst` using `ctx`."""
        t = (env or self.env).get_template(template_name)
        c = ctx or {}
        self.write(self.abspath(dst), t.render(**c), overwrite=overwrite)

    def write_yaml(self, dst, dto):
        self.write(dst, yaml.safe_dump(dto, indent=2, default_flow_style=False))


class Package(CodeRepository):

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        super().__init__(*args, **kwargs)

    def relpath(self, path):
        return os.path.join(f'./{self.name}', path)

    def mkdir(self, path):
        super(Package, self).mkdir(path)
        parts = path.split('/')
        for i, part in enumerate(parts):
            dst = self.join('/'.join(parts[:i+1]), '__init__.py')
            os.system(f'touch {dst}')
            self.vcs.index.add([dst])
