# Copyright (C) 2017-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""This document contains a SWH loader for ingesting repository data
from Mercurial version 2 bundle files.

"""

# NOTE: The code here does expensive work twice in places because of the
# intermediate need to check for what is missing before sending to the database
# and the desire to not juggle very large amounts of data.

# TODO: Decide whether to also serialize to disk and read back more quickly
#       from there. Maybe only for very large repos and fast drives.
# - Avi


import datetime
import hglib
import os
import random
import re

from dateutil import parser
from shutil import rmtree
from tempfile import mkdtemp

from swh.model import identifiers
from swh.model.hashutil import (
    MultiHash, hash_to_hex, hash_to_bytes,
    DEFAULT_ALGORITHMS
)
from swh.loader.core.loader import UnbufferedLoader
from swh.loader.core.converters import content_for_storage
from swh.loader.core.utils import clean_dangling_folders

from . import converters
from .archive_extract import tmp_extract
from .bundle20_reader import Bundle20Reader
from .converters import PRIMARY_ALGO as ALGO
from .objects import SelectiveCache, SimpleTree


TAG_PATTERN = re.compile('[0-9A-Fa-f]{40}')

TEMPORARY_DIR_PREFIX_PATTERN = 'swh.loader.mercurial.'

HEAD_POINTER_NAME = b'tip'


class HgBundle20Loader(UnbufferedLoader):
    """Mercurial loader able to deal with remote or local repository.

    """
    CONFIG_BASE_FILENAME = 'loader/mercurial'

    ADDITIONAL_CONFIG = {
        'bundle_filename': ('str', 'HG20_none_bundle'),
        'reduce_effort': ('bool', False),
        'temp_directory': ('str', '/tmp'),
        'cache1_size': ('int', 800*1024*1024),
        'cache2_size': ('int', 800*1024*1024),
    }

    def __init__(self, logging_class='swh.loader.mercurial.Bundle20Loader'):
        super().__init__(logging_class=logging_class)
        self.content_max_size_limit = self.config['content_size_limit']
        self.bundle_filename = self.config['bundle_filename']
        self.reduce_effort_flag = self.config['reduce_effort']
        self.empty_repository = None
        self.temp_directory = self.config['temp_directory']
        self.cache1_size = self.config['cache1_size']
        self.cache2_size = self.config['cache2_size']
        self.working_directory = None
        self.bundle_path = None

    def pre_cleanup(self):
        """Cleanup potential dangling files from prior runs (e.g. OOM killed
           tasks)

        """
        clean_dangling_folders(self.temp_directory,
                               pattern_check=TEMPORARY_DIR_PREFIX_PATTERN,
                               log=self.log)

    def cleanup(self):
        """Clean temporary working directory

        """
        if self.bundle_path and os.path.exists(self.bundle_path):
            self.log.debug('Cleanup up working bundle %s' % self.bundle_path)
            os.unlink(self.bundle_path)
        if self.working_directory and os.path.exists(self.working_directory):
            self.log.debug('Cleanup up working directory %s' % (
                self.working_directory, ))
            rmtree(self.working_directory)

    def get_heads(self, repo):
        """Read the closed branches heads (branch, bookmarks) and returns a
           dict with key the branch_name (bytes) and values the tuple
           (pointer nature (bytes), mercurial's node id
           (bytes)). Those needs conversion to swh-ids. This is taken
           care of in get_revisions.

        """
        b = {}
        for _, node_hash_id, pointer_nature, branch_name, *_ in repo.heads():
            b[branch_name] = (
                pointer_nature, hash_to_bytes(node_hash_id.decode()))

        bookmarks = repo.bookmarks()
        if bookmarks and bookmarks[0]:
            for bookmark_name, _, target_short in bookmarks[0]:
                target = repo[target_short].node()
                b[bookmark_name] = (None, hash_to_bytes(target.decode()))

        return b

    def prepare_origin_visit(self, *, origin_url, visit_date, **kwargs):
        self.origin_url = origin_url
        self.origin = {'url': self.origin_url, 'type': 'hg'}
        if isinstance(visit_date, str):  # visit_date can be string or datetime
            visit_date = parser.parse(visit_date)
        self.visit_date = visit_date

    def prepare(self, *, origin_url, visit_date, directory=None):
        """Prepare the necessary steps to load an actual remote or local
           repository.

           To load a local repository, pass the optional directory
           parameter as filled with a path to a real local folder.

           To load a remote repository, pass the optional directory
           parameter as None.

        Args:
            origin_url (str): Origin url to load
            visit_date (str/datetime): Date of the visit
            directory (str/None): The local directory to load

        """
        self.branches = {}
        self.tags = []
        self.releases = {}
        self.node_2_rev = {}

        if not directory:  # remote repository
            self.working_directory = mkdtemp(
                prefix=TEMPORARY_DIR_PREFIX_PATTERN,
                suffix='-%s' % os.getpid(),
                dir=self.temp_directory)
            os.makedirs(self.working_directory, exist_ok=True)
            self.hgdir = self.working_directory

            self.log.debug('Cloning %s to %s' % (
                self.origin['url'], self.hgdir))
            hglib.clone(source=self.origin['url'], dest=self.hgdir)
        else:  # local repository
            self.working_directory = None
            self.hgdir = directory

        self.bundle_path = os.path.join(self.hgdir, self.bundle_filename)
        self.log.debug('Bundling at %s' % self.bundle_path)
        with hglib.open(self.hgdir) as repo:
            self.heads = self.get_heads(repo)
            repo.bundle(bytes(self.bundle_path, 'utf-8'),
                        all=True,
                        type=b'none-v2')

        self.cache_filename1 = os.path.join(
            self.hgdir, 'swh-cache-1-%s' % (
                hex(random.randint(0, 0xffffff))[2:], ))
        self.cache_filename2 = os.path.join(
            self.hgdir, 'swh-cache-2-%s' % (
                hex(random.randint(0, 0xffffff))[2:], ))

        try:
            self.br = Bundle20Reader(bundlefile=self.bundle_path,
                                     cache_filename=self.cache_filename1,
                                     cache_size=self.cache1_size)
        except FileNotFoundError:
            # Empty repository! Still a successful visit targeting an
            # empty snapshot
            self.log.warn('%s is an empty repository!' % self.hgdir)
            self.empty_repository = True
        else:
            self.reduce_effort = set()
            if self.reduce_effort_flag:
                now = datetime.datetime.now(tz=datetime.timezone.utc)
                if (now - self.visit_date).days > 1:
                    # Assuming that self.visit_date would be today for
                    # a new visit, treat older visit dates as
                    # indication of wanting to skip some processing
                    # effort.
                    for header, commit in self.br.yield_all_changesets():
                        ts = commit['time'].timestamp()
                        if ts < self.visit_date.timestamp():
                            self.reduce_effort.add(header['node'])

    def has_contents(self):
        return not self.empty_repository

    def has_directories(self):
        return not self.empty_repository

    def has_revisions(self):
        return not self.empty_repository

    def has_releases(self):
        return not self.empty_repository

    def fetch_data(self):
        """Fetch the data from the data source."""
        pass

    def get_contents(self):
        """Get the contents that need to be loaded."""

        # NOTE: This method generates blobs twice to reduce memory usage
        # without generating disk writes.
        self.file_node_to_hash = {}
        hash_to_info = {}
        self.num_contents = 0
        contents = {}
        missing_contents = set()

        for blob, node_info in self.br.yield_all_blobs():
            self.num_contents += 1
            file_name = node_info[0]
            header = node_info[2]

            length = len(blob)
            if header['linknode'] in self.reduce_effort:
                algorithms = [ALGO]
            else:
                algorithms = DEFAULT_ALGORITHMS
            h = MultiHash.from_data(blob, hash_names=algorithms)
            content = h.digest()
            content['length'] = length
            blob_hash = content[ALGO]
            self.file_node_to_hash[header['node']] = blob_hash

            if header['linknode'] in self.reduce_effort:
                continue

            hash_to_info[blob_hash] = node_info
            contents[blob_hash] = content
            missing_contents.add(blob_hash)

            if file_name == b'.hgtags':
                # https://www.mercurial-scm.org/wiki/GitConcepts#Tag_model
                # overwrite until the last one
                self.tags = (t for t in blob.split(b'\n') if t != b'')

        if contents:
            missing_contents = set(
                self.storage.content_missing(
                    list(contents.values()),
                    key_hash=ALGO
                )
            )

        # Clusters needed blobs by file offset and then only fetches the
        # groups at the needed offsets.
        focs = {}  # "file/offset/contents"
        for blob_hash in missing_contents:
            _, file_offset, header = hash_to_info[blob_hash]
            focs.setdefault(file_offset, {})
            focs[file_offset][header['node']] = blob_hash

        hash_to_info = None
        for offset, node_hashes in sorted(focs.items()):
            for header, data, *_ in self.br.yield_group_objects(
                group_offset=offset
            ):
                node = header['node']
                if node in node_hashes:
                    blob, meta = self.br.extract_meta_from_blob(data)
                    content = contents.pop(node_hashes[node], None)
                    if content:
                        content['data'] = blob
                        yield content_for_storage(
                            content,
                            log=self.log,
                            max_content_size=self.content_max_size_limit,
                            origin_url=self.origin['url']
                        )

    def load_directories(self):
        """This is where the work is done to convert manifest deltas from the
        repository bundle into SWH directories.

        """
        self.mnode_to_tree_id = {}
        cache_hints = self.br.build_manifest_hints()

        def tree_size(t):
            return t.size()

        self.trees = SelectiveCache(cache_hints=cache_hints,
                                    size_function=tree_size,
                                    filename=self.cache_filename2,
                                    max_size=self.cache2_size)

        tree = SimpleTree()
        for header, added, removed in self.br.yield_all_manifest_deltas(
            cache_hints
        ):
            node = header['node']
            basenode = header['basenode']
            tree = self.trees.fetch(basenode) or tree  # working tree

            for path in removed.keys():
                tree = tree.remove_tree_node_for_path(path)
            for path, info in added.items():
                file_node, is_symlink, perms_code = info
                tree = tree.add_blob(
                    path,
                    self.file_node_to_hash[file_node],
                    is_symlink,
                    perms_code
                )

            if header['linknode'] in self.reduce_effort:
                self.trees.store(node, tree)
            else:
                new_dirs = []
                self.mnode_to_tree_id[node] = tree.hash_changed(new_dirs)
                self.trees.store(node, tree)
                yield header, tree, new_dirs

    def get_directories(self):
        """Compute directories to load

        """
        dirs = {}
        self.num_directories = 0
        for _, _, new_dirs in self.load_directories():
            for d in new_dirs:
                self.num_directories += 1
                dirs[d['id']] = d

        missing_dirs = list(dirs.keys())
        if missing_dirs:
            missing_dirs = self.storage.directory_missing(missing_dirs)

        for _id in missing_dirs:
            yield dirs[_id]
        dirs = {}

    def get_revisions(self):
        """Compute revisions to load

        """
        revisions = {}
        self.num_revisions = 0
        for header, commit in self.br.yield_all_changesets():
            if header['node'] in self.reduce_effort:
                continue

            self.num_revisions += 1
            date_dict = identifiers.normalize_timestamp(
                int(commit['time'].timestamp())
            )
            author_dict = converters.parse_author(commit['user'])
            if commit['manifest'] == Bundle20Reader.NAUGHT_NODE:
                directory_id = SimpleTree().hash_changed()
            else:
                directory_id = self.mnode_to_tree_id[commit['manifest']]

            extra_meta = []
            extra = commit.get('extra')
            if extra:
                for e in extra.split(b'\x00'):
                    k, v = e.split(b':', 1)
                    k = k.decode('utf-8')
                    # transplant_source stores binary reference to a changeset
                    # prefer to dump hexadecimal one in the revision metadata
                    if k == 'transplant_source':
                        v = hash_to_hex(v)
                    extra_meta.append([k, v])

            revision = {
                'author': author_dict,
                'date': date_dict,
                'committer': author_dict,
                'committer_date': date_dict,
                'type': 'hg',
                'directory': directory_id,
                'message': commit['message'],
                'metadata': {
                    'node': hash_to_hex(header['node']),
                    'extra_headers': [
                        ['time_offset_seconds',
                         str(commit['time_offset_seconds']).encode('utf-8')],
                    ] + extra_meta
                },
                'synthetic': False,
                'parents': []
            }

            p1 = self.node_2_rev.get(header['p1'])
            p2 = self.node_2_rev.get(header['p2'])
            if p1:
                revision['parents'].append(p1)
            if p2:
                revision['parents'].append(p2)

            revision['id'] = hash_to_bytes(
                identifiers.revision_identifier(revision)
            )
            self.node_2_rev[header['node']] = revision['id']
            revisions[revision['id']] = revision

        # Converts heads to use swh ids
        self.heads = {
            branch_name: (pointer_nature, self.node_2_rev[node_id])
            for branch_name, (pointer_nature, node_id) in self.heads.items()
        }

        missing_revs = revisions.keys()
        if missing_revs:
            missing_revs = set(
                self.storage.revision_missing(list(missing_revs))
            )

        for r in missing_revs:
            yield revisions[r]
        self.mnode_to_tree_id = None

    def _read_tag(self, tag, split_byte=b' '):
        node, *name = tag.split(split_byte)
        name = split_byte.join(name)
        return node, name

    def get_releases(self):
        """Get the releases that need to be loaded."""
        self.num_releases = 0
        releases = {}
        missing_releases = []
        for t in self.tags:
            self.num_releases += 1
            node, name = self._read_tag(t)
            node = node.decode()
            node_bytes = hash_to_bytes(node)
            if not TAG_PATTERN.match(node):
                self.log.warn('Wrong pattern (%s) found in tags. Skipping' % (
                    node, ))
                continue
            if node_bytes not in self.node_2_rev:
                self.log.warn('No matching revision for tag %s '
                              '(hg changeset: %s). Skipping' %
                              (name.decode(), node))
                continue
            tgt_rev = self.node_2_rev[node_bytes]
            release = {
                'name': name,
                'target': tgt_rev,
                'target_type': 'revision',
                'message': None,
                'metadata': None,
                'synthetic': False,
                'author': {'name': None, 'email': None, 'fullname': b''},
                'date': None
            }
            id_hash = hash_to_bytes(
                identifiers.release_identifier(release))
            release['id'] = id_hash
            missing_releases.append(id_hash)
            releases[id_hash] = release
            self.releases[name] = id_hash

        if missing_releases:
            missing_releases = set(
                self.storage.release_missing(missing_releases))

        for _id in missing_releases:
            yield releases[_id]

    def get_snapshot(self):
        """Get the snapshot that need to be loaded."""
        branches = {}
        for name, (pointer_nature, target) in self.heads.items():
            branches[name] = {'target': target, 'target_type': 'revision'}
            if pointer_nature == HEAD_POINTER_NAME:
                branches[b'HEAD'] = {'target': name, 'target_type': 'alias'}
        for name, target in self.releases.items():
            branches[name] = {'target': target, 'target_type': 'release'}

        snap = {
            'id': None,
            'branches': branches,
        }
        snap['id'] = identifiers.identifier_to_bytes(
            identifiers.snapshot_identifier(snap))
        return snap

    def get_fetch_history_result(self):
        """Return the data to store in fetch_history."""
        return {
            'contents': self.num_contents,
            'directories': self.num_directories,
            'revisions': self.num_revisions,
            'releases': self.num_releases,
        }


class HgArchiveBundle20Loader(HgBundle20Loader):
    """Mercurial loader for repository wrapped within archives.

    """
    def __init__(self):
        super().__init__(
            logging_class='swh.loader.mercurial.HgArchiveBundle20Loader')
        self.temp_dir = None

    def prepare(self, *, origin_url, archive_path, visit_date):
        self.temp_dir = tmp_extract(archive=archive_path,
                                    dir=self.temp_directory,
                                    prefix=TEMPORARY_DIR_PREFIX_PATTERN,
                                    suffix='.dump-%s' % os.getpid(),
                                    log=self.log,
                                    source=origin_url)

        repo_name = os.listdir(self.temp_dir)[0]
        directory = os.path.join(self.temp_dir, repo_name)
        super().prepare(origin_url=origin_url,
                        visit_date=visit_date, directory=directory)

    def cleanup(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            rmtree(self.temp_dir)
        super().cleanup()
