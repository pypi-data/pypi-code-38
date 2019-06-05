# repo.py -- For dealing with git repositories.
# Copyright (C) 2007 James Westby <jw+debian@jameswestby.net>
# Copyright (C) 2008-2013 Jelmer Vernooij <jelmer@samba.org>
#
# Dulwich is dual-licensed under the Apache License, Version 2.0 and the GNU
# General Public License as public by the Free Software Foundation; version 2.0
# or (at your option) any later version. You can redistribute it and/or
# modify it under the terms of either of these two licenses.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You should have received a copy of the licenses; if not, see
# <http://www.gnu.org/licenses/> for a copy of the GNU General Public License
# and <http://www.apache.org/licenses/LICENSE-2.0> for a copy of the Apache
# License, Version 2.0.
#


"""Repository access.

This module contains the base class for git repositories
(BaseRepo) and an implementation which uses a repository on
local disk (Repo).

"""

from io import BytesIO
import errno
import os
import sys
import stat

import time

from .errors import (
    NoIndexPresent,
    NotBlobError,
    NotCommitError,
    NotTreeError,
    NotTagError,
    RefFormatError,
)
from .file import (
    GitFile,
)
from .objects import (
    check_hexsha,
    Blob,
    Commit,
    ShaFile,
    Tag,
    Tree,
)


from .refs import (  # noqa: F401
    DictRefsContainer,
    DiskRefsContainer,
)

import warnings

os_sep_bytes = os.sep.encode('ascii')

OBJECTDIR = 'objects'
REFSDIR = 'refs'
REFSDIR_TAGS = 'tags'
REFSDIR_HEADS = 'heads'
INDEX_FILENAME = "index"
CONFIG_FILENAME = "config"
COMMONDIR = 'commondir'
GITDIR = 'gitdir'
WORKTREES = 'worktrees'

BASE_DIRECTORIES = [
    ["branches"],
    [REFSDIR],
    [REFSDIR, REFSDIR_TAGS],
    [REFSDIR, REFSDIR_HEADS],
    ["hooks"],
    ["info"]
]

DEFAULT_REF = b'refs/heads/master'


def parse_graftpoints(graftpoints):
    """Convert a list of graftpoints into a dict

    :param graftpoints: Iterator of graftpoint lines

    Each line is formatted as:
        <commit sha1> <parent sha1> [<parent sha1>]*

    Resulting dictionary is:
        <commit sha1>: [<parent sha1>*]

    https://git.wiki.kernel.org/index.php/GraftPoint
    """
    grafts = {}
    for l in graftpoints:
        raw_graft = l.split(None, 1)

        commit = raw_graft[0]
        if len(raw_graft) == 2:
            parents = raw_graft[1].split()
        else:
            parents = []

        for sha in [commit] + parents:
            check_hexsha(sha, 'Invalid graftpoint')

        grafts[commit] = parents
    return grafts


def serialize_graftpoints(graftpoints):
    """Convert a dictionary of grafts into string

    The graft dictionary is:
        <commit sha1>: [<parent sha1>*]

    Each line is formatted as:
        <commit sha1> <parent sha1> [<parent sha1>]*

    https://git.wiki.kernel.org/index.php/GraftPoint

    """
    graft_lines = []
    for commit, parents in graftpoints.items():
        if parents:
            graft_lines.append(commit + b' ' + b' '.join(parents))
        else:
            graft_lines.append(commit)
    return b'\n'.join(graft_lines)


def blob_from_path_and_stat(fs_path, st):
    """Create a blob from a path and a stat object.

    :param fs_path: Full file system path to file
    :param st: A stat object
    :return: A `Blob` object
    """
    assert isinstance(fs_path, bytes)
    blob = Blob()
    if not stat.S_ISLNK(st.st_mode):
        with open(fs_path, 'rb') as f:
            blob.data = f.read()
    else:
        if sys.platform == 'win32' and sys.version_info[0] == 3:
            # os.readlink on Python3 on Windows requires a unicode string.
            # TODO(jelmer): Don't assume tree_encoding == fs_encoding
            tree_encoding = sys.getfilesystemencoding()
            fs_path = fs_path.decode(tree_encoding)
            blob.data = os.readlink(fs_path).encode(tree_encoding)
        else:
            blob.data = os.readlink(fs_path)

    return blob


def blob_from_reference_path(fs_path):
    assert isinstance(fs_path, bytes)

    if os.path.isdir(fs_path):
        raise ValueError('%s is a directory' % fs_path)

    blob = Blob()
    blob.data = fs_path

    return blob


def _fs_to_tree_path(fs_path, fs_encoding=None):
    """Convert a file system path to a git tree path.

    :param fs_path: File system path.
    :param fs_encoding: File system encoding

    :return:  Git tree path as bytes
    """
    if fs_encoding is None:
        fs_encoding = sys.getfilesystemencoding()
    if not isinstance(fs_path, bytes):
        fs_path_bytes = fs_path.encode(fs_encoding)
    else:
        fs_path_bytes = fs_path
    if os_sep_bytes != b'/':
        tree_path = fs_path_bytes.replace(os_sep_bytes, b'/')
    else:
        tree_path = fs_path_bytes
    return tree_path


class BaseRepo(object):
    """Base class for a git repository.

    :ivar object_store: Dictionary-like object for accessing
        the objects
    :ivar refs: Dictionary-like object with the refs in this
        repository
    """

    def __init__(self, object_store, refs):
        """Open a repository.

        This shouldn't be called directly, but rather through one of the
        base classes, such as MemoryRepo or Repo.

        :param object_store: Object store to use
        :param refs: Refs container to use
        """
        self._object_store = object_store
        self._refs = refs

    @property
    def object_store(self):
        if self._object_store is None:
            self._object_store = self.create_object_store()

        return self._object_store

    def create_object_store(self):
        pass

    def _determine_file_mode(self):
        """Probe the file-system to determine whether permissions can be trusted.

        :return: True if permissions can be trusted, False otherwise.
        """
        raise NotImplementedError(self._determine_file_mode)

    def _init_files(self, bare):
        """Initialize a default set of named files."""
        from .config import ConfigFile
        self._put_named_file('description', b"Unnamed repository")
        f = BytesIO()
        cf = ConfigFile()
        cf.set(b"core", b"repositoryformatversion", b"0")
        if self._determine_file_mode():
            cf.set(b"core", b"filemode", True)
        else:
            cf.set(b"core", b"filemode", False)

        cf.set(b"core", b"bare", bare)
        cf.set(b"core", b"logallrefupdates", True)
        cf.write_to_file(f)
        self._put_named_file('config', f.getvalue())
        self._put_named_file(os.path.join('info', 'exclude'), b'')

    def _put_named_file(self, path, contents):
        """Write a file to the control dir with the given name and contents.

        :param path: The path to the file, relative to the control dir.
        :param contents: A string to write to the file.
        """
        raise NotImplementedError(self._put_named_file)

    def open_index(self):
        """Open the index for this repository.

        :raise NoIndexPresent: If no index is present
        :return: The matching `Index`
        """
        raise NotImplementedError(self.open_index)

    def get_refs(self):
        """Get dictionary with all refs.

        :return: A ``dict`` mapping ref names to SHA1s
        """
        return self.refs.as_dict()

    def head(self):
        """Return the SHA1 pointed at by HEAD."""
        return self.refs[b'HEAD']

    def _get_object(self, sha, cls):
        assert len(sha) in (20, 40)
        ret = self.get_object(sha)
        if not isinstance(ret, cls):
            if cls is Commit:
                raise NotCommitError(ret)
            elif cls is Blob:
                raise NotBlobError(ret)
            elif cls is Tree:
                raise NotTreeError(ret)
            elif cls is Tag:
                raise NotTagError(ret)
            else:
                raise Exception("Type invalid: %r != %r" % (
                    ret.type_name, cls.type_name))
        return ret

    def get_object(self, sha):
        """Retrieve the object with the specified SHA.

        :param sha: SHA to retrieve
        :return: A ShaFile object
        :raise KeyError: when the object can not be found
        """
        return self.object_store[sha]

    def get_parents(self, sha, commit=None):
        """Retrieve the parents of a specific commit.

        If the specific commit is a graftpoint, the graft parents
        will be returned instead.

        :param sha: SHA of the commit for which to retrieve the parents
        :param commit: Optional commit matching the sha
        :return: List of parents
        """

        try:
            return self._graftpoints[sha]
        except KeyError:
            if commit is None:
                commit = self[sha]
            return commit.parents

    def get_config(self):
        """Retrieve the config object.

        :return: `ConfigFile` object for the ``.git/config`` file.
        """
        raise NotImplementedError(self.get_config)

    def set_description(self, description):
        """Set the description for this repository.

        :param description: Text to set as description for this repository.
        """
        raise NotImplementedError(self.set_description)

    def get_config_stack(self):
        """Return a config stack for this repository.

        This stack accesses the configuration for both this repository
        itself (.git/config) and the global configuration, which usually
        lives in ~/.gitconfig.

        :return: `Config` instance for this repository
        """
        from .config import StackedConfig
        backends = [self.get_config()] + StackedConfig.default_backends()
        return StackedConfig(backends, writable=backends[0])

    def get_peeled(self, ref):
        """Get the peeled value of a ref.

        :param ref: The refname to peel.
        :return: The fully-peeled SHA1 of a tag object, after peeling all
            intermediate tags; if the original ref does not point to a tag,
            this will equal the original SHA1.
        """
        cached = self.refs.get_peeled(ref)
        if cached is not None:
            return cached
        return self.object_store.peel_sha(self.refs[ref]).id

    def get_walker(self, include=None, *args, **kwargs):
        """Obtain a walker for this repository.

        :param include: Iterable of SHAs of commits to include along with their
            ancestors. Defaults to [HEAD]
        :param exclude: Iterable of SHAs of commits to exclude along with their
            ancestors, overriding includes.
        :param order: ORDER_* constant specifying the order of results.
            Anything other than ORDER_DATE may result in O(n) memory usage.
        :param reverse: If True, reverse the order of output, requiring O(n)
            memory.
        :param max_entries: The maximum number of entries to yield, or None for
            no limit.
        :param paths: Iterable of file or subtree paths to show entries for.
        :param rename_detector: diff.RenameDetector object for detecting
            renames.
        :param follow: If True, follow path across renames/copies. Forces a
            default rename_detector.
        :param since: Timestamp to list commits after.
        :param until: Timestamp to list commits before.
        :param queue_cls: A class to use for a queue of commits, supporting the
            iterator protocol. The constructor takes a single argument, the
            Walker.
        :return: A `Walker` object
        """
        from .walk import Walker
        if include is None:
            include = [self.head()]
        if isinstance(include, str):
            include = [include]

        kwargs['get_parents'] = lambda commit: self.get_parents(
            commit.id, commit)

        return Walker(self.object_store, include, *args, **kwargs)

    def __getitem__(self, name):
        """Retrieve a Git object by SHA1 or ref.

        :param name: A Git object SHA1 or a ref name
        :return: A `ShaFile` object, such as a Commit or Blob
        :raise KeyError: when the specified ref or object does not exist
        """
        if not isinstance(name, bytes):
            raise TypeError("'name' must be bytestring, not %.80s" %
                            type(name).__name__)
        if len(name) in (20, 40):
            try:
                return self.object_store[name]
            except (KeyError, ValueError):
                pass
        try:
            return self.object_store[self.refs[name]]
        except RefFormatError:
            raise KeyError(name)

    def __contains__(self, name):
        """Check if a specific Git object or ref is present.

        :param name: Git object SHA1 or ref name
        """
        if len(name) in (20, 40):
            return name in self.object_store or name in self.refs
        else:
            return name in self.refs

    def __setitem__(self, name, value):
        """Set a ref.

        :param name: ref name
        :param value: Ref value - either a ShaFile object, or a hex sha
        """
        if name.startswith(b"refs/") or name == b'HEAD':
            if isinstance(value, ShaFile):
                self.refs[name] = value.id
            elif isinstance(value, bytes):
                self.refs[name] = value
            else:
                raise TypeError(value)
        else:
            raise ValueError(name)

    def __delitem__(self, name):
        """Remove a ref.

        :param name: Name of the ref to remove
        """
        if name.startswith(b"refs/") or name == b"HEAD":
            del self.refs[name]
        else:
            raise ValueError(name)

    def _get_user_identity(self):
        """Determine the identity to use for new commits.
        """
        config = self.get_config_stack()
        return config.get((b"user",), b"name") + b" <" + config.get((b"user",), b"email") + b">"

    def _add_graftpoints(self, updated_graftpoints):
        """Add or modify graftpoints

        :param updated_graftpoints: Dict of commit shas to list of parent shas
        """

        # Simple validation
        for commit, parents in updated_graftpoints.items():
            for sha in [commit] + parents:
                check_hexsha(sha, 'Invalid graftpoint')

        self._graftpoints.update(updated_graftpoints)

    def _remove_graftpoints(self, to_remove=[]):
        """Remove graftpoints

        :param to_remove: List of commit shas
        """
        for sha in to_remove:
            del self._graftpoints[sha]

    def get_ignore_filter_manager(self):
        from .ignore import IgnoreFilterManager

        return IgnoreFilterManager.from_repo(self)


class Repo(BaseRepo):
    """A git repository backed by local disk.

    To open an existing repository, call the contructor with
    the path of the repository.

    To create a new repository, use the Repo.init class method.
    """

    def __init__(self, repo_config_root):
        self._repo_config_root = repo_config_root

        BaseRepo.__init__(self, None, None)

    def _determine_file_mode(self):
        """Probe the file-system to determine whether permissions can be trusted.

        :return: True if permissions can be trusted, False otherwise.
        """
        fname = os.path.join(self.path, '.probe-permissions')
        with open(fname, 'w') as f:
            f.write('')

        st1 = os.lstat(fname)
        os.chmod(fname, st1.st_mode ^ stat.S_IXUSR)
        st2 = os.lstat(fname)

        os.unlink(fname)

        mode_differs = st1.st_mode != st2.st_mode
        st2_has_exec = (st2.st_mode & stat.S_IXUSR) != 0

        return mode_differs and st2_has_exec

    def _put_named_file(self, path, contents):
        """Write a file to the control dir with the given name and contents.

        :param path: The path to the file, relative to the control dir.
        :param contents: A string to write to the file.
        """
        path = path.lstrip(os.path.sep)
        with GitFile(os.path.join(self.controldir(), path), 'wb') as f:
            f.write(contents)

    def index_path(self):
        """Return path to the index file."""
        return os.path.join(self.controldir(), INDEX_FILENAME)

    def open_index(self):
        """Open the index for this repository.

        :raise NoIndexPresent: If no index is present
        :return: The matching `Index`
        """
        from .index import Index
        if not self.has_index():
            raise NoIndexPresent()
        return Index(self.index_path())

    def has_index(self):
        """Check if an index is present."""
        # Bare repos must never have index files; non-bare repos may have a
        # missing index file, which is treated as empty.
        return not self.bare

    class UploadFileRequest(object):
        def __init__(self, index_file_info):
            full_path = index_file_info['path']

            self.full_path = full_path
            self.rel_path = index_file_info['name']

            self.content_type = index_file_info.get('content_type')
            self.sha = index_file_info['sha']

            self.size = index_file_info['size']

            self.st = os.stat_result((
                0,  # mode
                0,  # inode
                0,  # device
                0,  # hard links
                0,  # owner uid
                0,  # gid
                index_file_info['size'],  # size
                0,  # atime
                time.mktime(index_file_info['mtime'].timetuple()),
                time.mktime(index_file_info.get('ctime', index_file_info['mtime']).timetuple()),
            ))

        @property
        def index_entry(self):
            from .index import index_entry_from_stat

            return index_entry_from_stat(self.st, self.sha, 0)

    @classmethod
    def _files_info_to_index_info(cls, file_info_or_index_files_info):
        index_info = {}

        index_info.update(file_info_or_index_files_info)

        if 'sha_get' in index_info:
            index_info['sha'] = index_info['sha_get']()
            del index_info['sha_get']

        if 'rel_file_name' in index_info:
            index_info['name'] = index_info['rel_file_name']
            del index_info['rel_file_name']

        return index_info

    def stage(self, files_info_or_index_files_info, callback=None, isolation_token=None):
        index = self.open_index()

        upload_requests = [Repo.UploadFileRequest(self._files_info_to_index_info(file_info_or_index_files_info)) for file_info_or_index_files_info in files_info_or_index_files_info]

        def create_on_file_uploaded(all_upload_requests):
            entries = {}

            def on_file_uploaded(upload_request):
                entries[upload_request.rel_path] = upload_request.index_entry

                if len(entries) == len(all_upload_requests):
                    index.set_entries_from_list_async(entries, isolation_token=isolation_token)

                if callback:
                    callback(upload_request)

            return on_file_uploaded

        self.object_store.add_objects_async(upload_requests, create_on_file_uploaded(upload_requests))

    def reset_index(self, tree=None):
        """Reset the index back to a specific tree.

        :param tree: Tree SHA to reset to, None for current HEAD tree.
        """
        from .index import (
            build_index_from_tree,
            validate_path_element_default,
            validate_path_element_ntfs,
        )
        if tree is None:
            tree = self[b'HEAD'].tree
        config = self.get_config()
        honor_filemode = config.get_boolean(
            'core', 'filemode', os.name != "nt")
        if config.get_boolean('core', 'core.protectNTFS', os.name == "nt"):
            validate_path_element = validate_path_element_ntfs
        else:
            validate_path_element = validate_path_element_default
        return build_index_from_tree(
            self.path, self.index_path(), self.object_store, tree,
            honor_filemode=honor_filemode,
            validate_path_element=validate_path_element)

    def get_config(self):
        """Retrieve the config object.

        :return: `ConfigFile` object for the ``.git/config`` file.
        """
        from .config import ConfigFile
        path = os.path.join(self._controldir, 'config')
        try:
            return ConfigFile.from_path(path)
        except (IOError, OSError) as e:
            if e.errno != errno.ENOENT:
                raise
            ret = ConfigFile()
            ret.path = path
            return ret

    def get_description(self):
        """Retrieve the description of this repository.

        :return: A string describing the repository or None.
        """
        path = os.path.join(self._controldir, 'description')
        try:
            with GitFile(path, 'rb') as f:
                return f.read()
        except (IOError, OSError) as e:
            if e.errno != errno.ENOENT:
                raise
            return None

    def set_description(self, description):
        """Set the description for this repository.

        :param description: Text to set as description for this repository.
        """

        self._put_named_file('description', description)

    def close(self):
        """Close any files opened by this repository."""
        if self._object_store is not None:
            self.object_store.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MemoryRepo(BaseRepo):
    """Repo that stores refs, objects, and named files in memory.

    MemoryRepos are always bare: they have no working tree and no index, since
    those have a stronger dependency on the filesystem.
    """

    def __init__(self):
        from .config import ConfigFile
        BaseRepo.__init__(self, MemoryObjectStore(), DictRefsContainer({}))
        self._named_files = {}
        self.bare = True
        self._config = ConfigFile()
        self._description = None

    def set_description(self, description):
        self._description = description

    def get_description(self):
        return self._description

    def _determine_file_mode(self):
        """Probe the file-system to determine whether permissions can be trusted.

        :return: True if permissions can be trusted, False otherwise.
        """
        return sys.platform != 'win32'

    def _put_named_file(self, path, contents):
        """Write a file to the control dir with the given name and contents.

        :param path: The path to the file, relative to the control dir.
        :param contents: A string to write to the file.
        """
        self._named_files[path] = contents

    def open_index(self):
        """Fail to open index for this repo, since it is bare.

        :raise NoIndexPresent: Raised when no index is present
        """
        raise NoIndexPresent()

    def get_config(self):
        """Retrieve the config object.

        :return: `ConfigFile` object.
        """
        return self._config

    @classmethod
    def init_bare(cls, objects, refs):
        """Create a new bare repository in memory.

        :param objects: Objects for the new repository,
            as iterable
        :param refs: Refs as dictionary, mapping names
            to object SHA1s
        """
        ret = cls()
        for obj in objects:
            ret.object_store.add_object(obj)
        for refname, sha in refs.items():
            ret.refs[refname] = sha
        ret._init_files(bare=True)
        return ret
