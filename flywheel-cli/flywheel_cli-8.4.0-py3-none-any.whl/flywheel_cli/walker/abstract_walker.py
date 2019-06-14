"""Abstract file-system walker class"""
import collections
import fnmatch

from abc import ABC, abstractmethod

class FileInfo(object):
    """Represents a node in a filesystem

    Attributes:
        name (str): The name of the file
        is_dir (bool): Whether or not the given entry is a directory
        created (datetime): When the file was created (optional)
        modified (datetime): The last time this file was modified (optional)
        size (integer): The size of the file in bytes
        is_link (bool): Whether or not this file is a symlink
    """
    def __init__(self, name, is_dir, created=None, modified=None, size=None, is_link=False):
        self.name = name
        self.is_dir = is_dir
        self.created = created
        self.modified = modified
        self.size = size
        self.is_link = is_link

    def __repr__(self):
        return 'FileInfo(name={}, is_dir={}, is_link={}, size={})'.format(
            self.name, self.is_dir, self.is_link, self.size)


class AbstractWalker(ABC):
    """Abstract interface for walking a filesystem"""
    def __init__(self, root, ignore_dot_files=True, follow_symlinks=False, filter=None, exclude=None,
            filter_dirs=None, exclude_dirs=None):
        """Initialize the abstract walker

        Args:
            root (str): The starting directory for walking
            ignore_dot_files (bool): Whether or not to ignore files starting with '.'
            follow_symlinks(bool): Whether or not to follow symlinks
            filter (list): An optional list of filename patterns to INCLUDE
            exclude (list): An optional list of filename patterns to EXCLUDE
            filter_dirs (list): An optional list of directories to INCLUDE
            exclude_dirs (list): An optional list of patterns of directories to EXCLUDE
        """
        self.root = root

        self._ignore_dot_files = ignore_dot_files
        self._follow_symlinks = follow_symlinks

        self._include_files = filter
        self._exclude_files = exclude

        self._include_dirs = filter_dirs
        if self._include_dirs:
            self._include_dirs = [spec.split('/') for spec in self._include_dirs]
        self._exclude_dirs = exclude_dirs

    def __repr__(self):
        include_files_str = ','.join(self._include_files) if self._include_files else '[]'
        exclude_files_str = ','.join(self._exclude_files) if self._exclude_files else '[]'
        include_dirs = ['/'.join(spec) for spec in self._include_dirs or []]
        include_dirs_str = ','.join(include_dirs) if include_dirs else '[]'
        exclude_dirs_str = ','.join(self._exclude_dirs) if self._exclude_dirs else '[]'

        return ('{}(root={}, ignore_dot_files={}, follow_symlinks={}, '
            'filter={}, exclude={}, filter_dirs={}, exclude_dirs={}').format(
            type(self).__name__, self.root, self._ignore_dot_files, self._follow_symlinks,
            include_files_str, exclude_files_str, include_dirs_str, exclude_dirs_str)

    @abstractmethod
    def get_fs_url(self):
        """Return the FS url for the underlying filesystem"""

    def walk(self, subdir=None, max_depth=None):
        """Recursively list files in a filesystem.

        Yields:
            tuple: containing root path, a list of directories, and list of files
        """
        queue = collections.deque()
        if subdir:
            subdir = self.combine(self.root, subdir)
        else:
            subdir = self.root

        queue.append((1, subdir))

        while queue:
            # Pop next off
            depth, root = queue.popleft()

            subdirs = []
            files = []

            for item in self._listdir(root):
                full_path = self.combine(root, item.name)
                if item.is_dir:
                    prefix_path = self.get_prefix_path(full_path)
                    if self._should_include_dir(prefix_path, item):
                        subdirs.append(item)

                        if max_depth is None or depth < max_depth:
                            queue.append((depth+1, full_path))
                elif self._should_include_file(item):
                    files.append(item)

            yield (root, subdirs, files)

    def get_prefix_path(self, root):
        if self.root == '':
            if '/' not in root:
                prefix_path = '/'
            else:
                prefix_path = root
        elif self.root == '/':
            prefix_path = root.lstrip('/')
        else:
            prefix_path = root.split(self.root)[1]

        return prefix_path

    def files(self, subdir=None, max_depth=None):
        """Return all files in the sub directory"""
        for root, _, files in self.walk(subdir=subdir, max_depth=max_depth):
            for file_info in files:
                prefix_path = self.get_prefix_path(root)
                yield self.combine(prefix_path, file_info.name)

    @abstractmethod
    def open(self, path, mode='rb', **kwargs):
        """Open the given path for reading.

        Params:
            path (str): The relative or full path of the file to open
            mode (str): The open mode, either 'r' or 'rb'
            kwargs: Additional arguments to pass to open (e.g. buffering)

        Returns:
            file: a file-like object, opened for reading
        """

    @abstractmethod
    def _listdir(self, path):
        """List the contents of the given directory

        Args:
            path (str): The absolute path to the directory to list

        Yields:
            list(FileInfo): A list of file info objects
        """

    def remove_prefix(self, subdir, path):
        """Strip subdir from the beginning of path"""
        if path.startswith(subdir):
            path = path[len(subdir):]
        return path.lstrip('/')
    def close(self):
        """Cleanup any resources on this walker"""

    def combine(self, part1, part2):
        """Combine two path parts with delim"""
        part1 = part1.rstrip('/')
        part2 = part2.lstrip('/')
        return part1 + '/' + part2

    def _match(self, patterns, name):
        """Return true if name matches any of the given patterns"""
        for pat in patterns:
            if fnmatch.fnmatch(name, pat):
                return True
        return False

    def _should_include_dir(self, path, info):
        """Check if the given directory should be included"""
        if self._ignore_dot_files and info.name.startswith('.'):
            return False

        if not self._follow_symlinks and info.is_link:
            return False

        if self._include_dirs is not None:
            parts = path.lstrip('/').split('/')
            if not filter_match(self._include_dirs, parts):
                return False

        if self._exclude_dirs is not None and self._match(self._exclude_dirs, info.name):
            return False

        return True

    def _should_include_file(self, info):
        """Check if the given file should be included"""
        if self._ignore_dot_files and info.name.startswith('.'):
            return False

        if self._exclude_files is not None and self._match(self._exclude_files, info.name):
            return False

        if self._include_files is not None and not self._match(self._include_files, info.name):
            return False

        return True

def filter_match(patterns, parts):
    """Check if any of the given patterns match the split path"""
    # Fast match - assumes that if the length of parts is
    # larger than the length of the pattern, then it already matched
    # previously
    count = len(parts)
    for pattern in patterns:
        pattern_count = len(pattern)
        if count <= pattern_count:
            for i in range(count):
                if not fnmatch.fnmatch(parts[i], pattern[i]):
                    return False
    return True
