"""
Files and directories
=====================
"""
from __future__ import print_function, with_statement

from pipes import quote
import os
from tempfile import mkstemp
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
import hashlib

import six

from fabric.api import run as _run, sudo as _sudo, abort, warn
from fabric.api import hide
from fabric.contrib.files import upload_template as _upload_template
from fabric.contrib.files import exists

from burlap.decorators import task
from burlap.utils import run_as_root
from burlap import ContainerSatchel

BLOCKSIZE = 2 ** 20 # 1MB

class watch:
    """
    Context manager to watch for changes to the contents of some files.

    The *filenames* argument can be either a string (single filename)
    or a list (multiple filenames).

    You can read the *changed* attribute at the end of the block to
    check if the contents of any of the watched files has changed.

    You can also provide a *callback* that will be called at the end of
    the block if the contents of any of the watched files has changed.

    Example using an explicit check::

        from fabric.contrib.files import comment, uncomment

        from burlap.files import watch
        from burlap.services import restart

        # Edit configuration file
        with watch('/etc/daemon.conf') as config:
            uncomment('/etc/daemon.conf', 'someoption')
            comment('/etc/daemon.conf', 'otheroption')

        # Restart daemon if needed
        if config.changed:
            restart('daemon')

    Same example using a callback::

        from functools import partial

        from fabric.contrib.files import comment, uncomment

        from burlap.files import watch
        from burlap.services import restart

        with watch('/etc/daemon.conf', callback=partial(restart, 'daemon')):
            uncomment('/etc/daemon.conf', 'someoption')
            comment('/etc/daemon.conf', 'otheroption')

    """

    def __init__(self, filenames, callback=None, use_sudo=False):
        if isinstance(filenames, six.string_types):
            self.filenames = [filenames]
        else:
            self.filenames = filenames
        self.callback = callback
        self.use_sudo = use_sudo
        self.digest = dict()
        self.changed = False

    def __enter__(self):
        with self.settings(hide('warnings')):
            for filename in self.filenames:
                self.digest[filename] = file.md5sum(filename, self.use_sudo)
        return self

    def __exit__(self, type, value, tb): # pylint: disable=redefined-builtin
        for filename in self.filenames:
            if self.md5sum(filename, self.use_sudo) != self.digest[filename]:
                self.changed = True
                break
        if self.changed and self.callback:
            self.callback()

class FileSatchel(ContainerSatchel):
    """
    Wrapper around common file operations.

    Note, most readonly actions ignore the global dryrun setting.
    """

    name = 'file'

    @task
    def is_file(self, path, use_sudo=False):
        """
        Check if a path exists, and is a file.
        """
        if self.is_local and not use_sudo:
            return os.path.isfile(path)
        func = use_sudo and _sudo or _run
        with self.settings(hide('running', 'warnings'), warn_only=True):
            return func('[ -f "%(path)s" ]' % locals()).succeeded

    @task
    def is_dir(self, path, use_sudo=False):
        """
        Check if a path exists, and is a directory.
        """
        if self.is_local and not use_sudo:
            return os.path.isdir(path)
        func = use_sudo and _sudo or _run
        with self.settings(hide('running', 'warnings'), warn_only=True):
            return func('[ -d "%(path)s" ]' % locals()).succeeded

    @task
    def is_link(self, path, use_sudo=False):
        """
        Check if a path exists, and is a symbolic link.
        """
        func = use_sudo and _sudo or _run
        with self.settings(hide('running', 'warnings'), warn_only=True):
            return func('[ -L "%(path)s" ]' % locals()).succeeded

    @task
    def get_owner(self, path, use_sudo=False):
        """
        Get the owner name of a file or directory.
        """
        func = use_sudo and run_as_root or self.run
        # I'd prefer to use quiet=True, but that's not supported with older
        # versions of Fabric.
        with self.settings(hide('running', 'stdout'), warn_only=True):
            result = func('stat -c %%U "%(path)s"' % locals())
            if result.failed and 'stat: illegal option' in result:
                # Try the BSD version of stat
                return func('stat -f %%Su "%(path)s"' % locals())
            return result

    @task
    def get_group(self, path, use_sudo=False):
        """
        Get the group name of a file or directory.
        """
        func = use_sudo and run_as_root or self.run
        # I'd prefer to use quiet=True, but that's not supported with older
        # versions of Fabric.
        with self.settings(hide('running', 'stdout'), warn_only=True):
            result = func('stat -c %%G "%(path)s"' % locals())
            if result.failed and 'stat: illegal option' in result:
                # Try the BSD version of stat
                return func('stat -f %%Sg "%(path)s"' % locals())
            return result

    def get_mode(self, path, use_sudo=False):
        """
        Get the mode (permissions) of a file or directory.

        Returns a string such as ``'0755'``, representing permissions as
        an octal number.
        """
        func = use_sudo and run_as_root or self.run
        # I'd prefer to use quiet=True, but that's not supported with older
        # versions of Fabric.
        with self.settings(hide('running', 'stdout'), warn_only=True):
            result = func('stat -c %%a "%(path)s"' % locals())
            if result.failed and 'stat: illegal option' in result:
                # Try the BSD version of stat
                return func('stat -f %%Op "%(path)s"|cut -c 4-6' % locals())
            return result

    @task
    def umask(self, use_sudo=False):
        """
        Get the user's umask.

        Returns a string such as ``'0002'``, representing the user's umask
        as an octal number.

        If `use_sudo` is `True`, this function returns root's umask.
        """
        func = use_sudo and run_as_root or self.run
        return func('umask')

    @task
    def upload_template(self, filename, destination, context=None, use_jinja=False,
                        template_dir=None, use_sudo=False, backup=True,
                        mirror_local_mode=False, mode=None,
                        mkdir=False, chown=False, user=None):
        """
        Upload a template file.

        This is a wrapper around :func:`fabric.contrib.files.upload_template`
        that adds some extra parameters.

        If ``mkdir`` is True, then the remote directory will be created, as
        the current user or as ``user`` if specified.

        If ``chown`` is True, then it will ensure that the current user (or
        ``user`` if specified) is the owner of the remote file.
        """

        if mkdir:
            remote_dir = os.path.dirname(destination)
            if use_sudo:
                self.sudo('mkdir -p %s' % quote(remote_dir), user=user)
            else:
                self.run('mkdir -p %s' % quote(remote_dir))

        if not self.dryrun:
            _upload_template(
                filename=filename,
                destination=destination,
                context=context,
                use_jinja=use_jinja,
                template_dir=template_dir,
                use_sudo=use_sudo,
                backup=backup,
                mirror_local_mode=mirror_local_mode,
                mode=mode,
            )

        if chown:
            if user is None:
                user = self.genv.user
            run_as_root('chown %s: %s' % (user, quote(destination)))

    @task
    def md5sum(self, filename, use_sudo=False):
        """
        Compute the MD5 sum of a file.
        """
        func = use_sudo and run_as_root or self.run
        with self.settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
            # Linux (LSB)
            if exists(u'/usr/bin/md5sum'):
                res = func(u'/usr/bin/md5sum %(filename)s' % locals())
            # BSD / OS X
            elif exists(u'/sbin/md5'):
                res = func(u'/sbin/md5 -r %(filename)s' % locals())
            # SmartOS Joyent build
            elif exists(u'/opt/local/gnu/bin/md5sum'):
                res = func(u'/opt/local/gnu/bin/md5sum %(filename)s' % locals())
            # SmartOS Joyent build
            # (the former doesn't exist, at least on joyent_20130222T000747Z)
            elif exists(u'/opt/local/bin/md5sum'):
                res = func(u'/opt/local/bin/md5sum %(filename)s' % locals())
            # Try to find ``md5sum`` or ``md5`` on ``$PATH`` or abort
            else:
                md5sum = func(u'which md5sum')
                md5 = func(u'which md5')
                if exists(md5sum):
                    res = func('%(md5sum)s %(filename)s' % locals())
                elif exists(md5):
                    res = func('%(md5)s %(filename)s' % locals())
                else:
                    abort('No MD5 utility was found on this system.')

        if res.succeeded:
            _md5sum = res
        else:
            warn(res)
            _md5sum = None

        if isinstance(_md5sum, six.string_types):
            _md5sum = _md5sum.strip().split('\n')[-1].split()[0]

        return _md5sum

    @task
    def uncommented_lines(self, filename, use_sudo=False):
        """
        Get the lines of a remote file, ignoring empty or commented ones
        """
        func = run_as_root if use_sudo else self.run
        res = func('cat %s' % quote(filename), quiet=True)
        if res.succeeded:
            return [line for line in res.splitlines() if line and not line.startswith('#')]
        return []


    def getmtime(self, path, use_sudo=False):
        """
        Return the time of last modification of path.
        The return value is a number giving the number of seconds since the epoch

        Same as :py:func:`os.path.getmtime()`
        """
        func = use_sudo and run_as_root or self.run
        with self.settings(hide('running', 'stdout')):
            return int(func('stat -c %%Y "%(path)s" ' % locals()).strip())

    @task
    def copy(self, source, destination, recursive=False, use_sudo=False):
        """
        Copy a file or directory
        """
        func = use_sudo and run_as_root or self.run
        options = '-r ' if recursive else ''
        func('/bin/cp {0}{1} {2}'.format(options, quote(source), quote(destination)))

    @task
    def move(self, source, destination, use_sudo=False):
        """
        Move a file or directory
        """
        func = use_sudo and run_as_root or self.run
        func('/bin/mv {0} {1}'.format(quote(source), quote(destination)))

    @task
    def symlink(self, source, destination, use_sudo=False):
        """
        Create a symbolic link to a file or directory
        """
        func = use_sudo and run_as_root or self.run
        func('/bin/ln -s {0} {1}'.format(quote(source), quote(destination)))

    @task
    def remove(self, path, recursive=False, use_sudo=False):
        """
        Remove a file or directory
        """
        func = use_sudo and run_as_root or self.run
        options = '-r ' if recursive else ''
        func('/bin/rm {0}{1}'.format(options, quote(path)))

    @task
    def upload(self, src, dst=None):
        dst = self.put_or_dryrun(local_path=src, remote_path=dst)
        print('Uploaded to %s' % (dst,))

    @task
    def download(self, src, dst=None):
        dst = self.get(local_path=dst, remote_path=src)
        print('Downloaded to %s' % (dst,))

    def require(self, path=None, contents=None, source=None, url=None, md5=None,
         use_sudo=False, owner=None, group='', mode=None, verify_remote=True,
         temp_dir='/tmp'):
        """
        Require a file to exist and have specific contents and properties.

        You can provide either:

        - *contents*: the required contents of the file::

            from fabtools import require

            require.file('/tmp/hello.txt', contents='Hello, world')

        - *source*: the local path of a file to upload::

            from fabtools import require

            require.file('/tmp/hello.txt', source='files/hello.txt')

        - *url*: the URL of a file to download (*path* is then optional)::

            from fabric.api import cd
            from fabtools import require

            with cd('tmp'):
                require.file(url='http://example.com/files/hello.txt')

        If *verify_remote* is ``True`` (the default), then an MD5 comparison
        will be used to check whether the remote file is the same as the
        source. If this is ``False``, the file will be assumed to be the
        same if it is present. This is useful for very large files, where
        generating an MD5 sum may take a while.

        When providing either the *contents* or the *source* parameter, Fabric's
        ``put`` function will be used to upload the file to the remote host.
        When ``use_sudo`` is ``True``, the file will first be uploaded to a temporary
        directory, then moved to its final location. The default temporary
        directory is ``/tmp``, but can be overridden with the *temp_dir* parameter.
        If *temp_dir* is an empty string, then the user's home directory will
        be used.

        If `use_sudo` is `True`, then the remote file will be owned by root,
        and its mode will reflect root's default *umask*. The optional *owner*,
        *group* and *mode* parameters can be used to override these properties.

        .. note:: This function can be accessed directly from the
                  ``fabtools.require`` module for convenience.

        """
        func = use_sudo and run_as_root or self.run

        # 1) Only a path is given
        if path and not (contents or source or url):
            assert path
            if not self.is_file(path):
                func('touch "%(path)s"' % locals())

        # 2) A URL is specified (path is optional)
        elif url:
            if not path:
                path = os.path.basename(urlparse(url).path)

            if not self.is_file(path) or md5 and self.md5sum(path) != md5:
                func('wget --progress=dot:mega "%(url)s" -O "%(path)s"' % locals())

        # 3) A local filename, or a content string, is specified
        else:
            if source:
                assert not contents
                t = None
            else:
                fd, source = mkstemp()
                t = os.fdopen(fd, 'w')
                t.write(contents)
                t.close()

            if verify_remote:
                # Avoid reading the whole file into memory at once
                digest = hashlib.md5()
                f = open(source, 'rb')
                try:
                    while True:
                        d = f.read(BLOCKSIZE)
                        if not d:
                            break
                        digest.update(d)
                finally:
                    f.close()
            else:
                digest = None

            if (not self.is_file(path, use_sudo=use_sudo) or
                    (verify_remote and
                        self.md5sum(path, use_sudo=use_sudo) != digest.hexdigest())):
                with self.settings(hide('running')):
                    self.put(local_path=source, remote_path=path, use_sudo=use_sudo, temp_dir=temp_dir)

            if t is not None:
                os.unlink(source)

        # Ensure correct owner
        if use_sudo and owner is None:
            owner = 'root'
        if (owner and self.get_owner(path, use_sudo) != owner) or \
           (group and self.get_group(path, use_sudo) != group):
            func('chown %(owner)s:%(group)s "%(path)s"' % locals())

        # Ensure correct mode
        if use_sudo and mode is None:
            mode = oct(0o666 & ~int(self.umask(use_sudo=True), base=8))
        if mode and self.get_mode(path, use_sudo) != mode:
            func('chmod %(mode)s "%(path)s"' % locals())

file = FileSatchel() # pylint: disable=redefined-builtin
