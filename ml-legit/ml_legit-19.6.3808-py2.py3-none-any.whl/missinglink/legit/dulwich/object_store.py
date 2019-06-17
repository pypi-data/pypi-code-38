# object_store.py -- Object store for git objects
# Copyright (C) 2008-2013 Jelmer Vernooij <jelmer@samba.org>
#                         and others
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


"""Git object store interfaces and implementation."""
import logging
from io import BytesIO
import errno
import os
import stat
import sys
import tempfile
from .diff_tree import (
    tree_changes,
    walk_trees,
    )
from .errors import (
    NotTreeError,
    )
from .file import GitFile
from .objects import (
    Commit,
    ShaFile,
    Tag,
    Tree,
    ZERO_SHA,
    sha_to_hex,
    hex_to_filename,
    S_ISGITLINK,
    object_class,
    )
from .pack import (
    Pack,
    PackData,
    PackInflater,
    iter_sha1,
    write_pack_header,
    write_pack_index_v2,
    write_pack_object,
    compute_file_sha,
    PackIndexer,
    PackStreamCopier,
    )

INFODIR = 'info'
PACKDIR = 'pack'


class BaseObjectStore(object):
    """Object store interface."""

    def determine_wants_all(self, refs):
        return [sha for (ref, sha) in refs.items()
                if sha not in self and not ref.endswith(b"^{}") and
                not sha == ZERO_SHA]

    def iter_shas(self, shas):
        """Iterate over the objects for the specified shas.

        :param shas: Iterable object with SHAs
        :return: Object iterator
        """
        return ObjectStoreIterator(self, shas)

    def get_raw(self, name):
        """Obtain the raw text for an object.

        :param name: sha for the object.
        :return: tuple with numeric type and object contents.
        """
        raise NotImplementedError(self.get_raw)

    def tree_changes(self, source, target, want_unchanged=False):
        """Find the differences between the contents of two trees

        :param source: SHA1 of the source tree
        :param target: SHA1 of the target tree
        :param want_unchanged: Whether unchanged files should be reported
        :return: Iterator over tuples with
            (oldpath, newpath), (oldmode, newmode), (oldsha, newsha)
        """
        for change in tree_changes(self, source, target,
                                   want_unchanged=want_unchanged):
            yield ((change.old.path, change.new.path),
                   (change.old.mode, change.new.mode),
                   (change.old.sha, change.new.sha))

    def iter_tree_contents(self, tree_id, include_trees=False):
        """Iterate the contents of a tree and all subtrees.

        Iteration is depth-first pre-order, as in e.g. os.walk.

        :param tree_id: SHA1 of the tree.
        :param include_trees: If True, include tree objects in the iteration.
        :return: Iterator over TreeEntry namedtuples for all the objects in a
            tree.
        """
        for entry, _ in walk_trees(self, tree_id, None):
            if not stat.S_ISDIR(entry.mode) or include_trees:
                yield entry

    def find_missing_objects(self, haves, wants, progress=None,
                             get_tagged=None,
                             get_parents=lambda commit: commit.parents):
        """Find the missing objects required for a set of revisions.

        :param haves: Iterable over SHAs already in common.
        :param wants: Iterable over SHAs of objects to fetch.
        :param progress: Simple progress function that will be called with
            updated progress strings.
        :param get_tagged: Function that returns a dict of pointed-to sha ->
            tag sha for including tags.
        :param get_parents: Optional function for getting the parents of a
            commit.
        :return: Iterator over (sha, path) pairs.
        """
        finder = MissingObjectFinder(self, haves, wants, progress, get_tagged,
                                     get_parents=get_parents)
        return iter(finder.next, None)

    def find_common_revisions(self, graphwalker):
        """Find which revisions this store has in common using graphwalker.

        :param graphwalker: A graphwalker object.
        :return: List of SHAs that are in common
        """
        haves = []
        sha = next(graphwalker)
        while sha:
            if sha in self:
                haves.append(sha)
                graphwalker.ack(sha)
            sha = next(graphwalker)
        return haves

    def generate_pack_contents(self, have, want, progress=None):
        """Iterate over the contents of a pack file.

        :param have: List of SHA1s of objects that should not be sent
        :param want: List of SHA1s of objects that should be sent
        :param progress: Optional progress reporting method
        """
        return self.iter_shas(self.find_missing_objects(have, want, progress))

    def peel_sha(self, sha):
        """Peel all tags from a SHA.

        :param sha: The object SHA to peel.
        :return: The fully-peeled SHA1 of a tag object, after peeling all
            intermediate tags; if the original ref does not point to a tag,
            this will equal the original SHA1.
        """
        obj = self[sha]
        obj_class = object_class(obj.type_name)
        while obj_class is Tag:
            obj_class, sha = obj.object
            obj = self[sha]
        return obj

    def _collect_ancestors(self, heads, common=set(),
                           get_parents=lambda commit: commit.parents):
        """Collect all ancestors of heads up to (excluding) those in common.

        :param heads: commits to start from
        :param common: commits to end at, or empty set to walk repository
            completely
        :param get_parents: Optional function for getting the parents of a
            commit.
        :return: a tuple (A, B) where A - all commits reachable
            from heads but not present in common, B - common (shared) elements
            that are directly reachable from heads
        """
        bases = set()
        commits = set()
        queue = []
        queue.extend(heads)
        while queue:
            e = queue.pop(0)
            if e in common:
                bases.add(e)
            elif e not in commits:
                commits.add(e)
                cmt = self[e]
                queue.extend(get_parents(cmt))
        return (commits, bases)

    def close(self):
        """Close any files opened by this object store."""
        # Default implementation is a NO-OP


class ObjectIterator(object):
    """Interface for iterating over objects."""

    def iterobjects(self):
        raise NotImplementedError(self.iterobjects)


class ObjectStoreIterator(ObjectIterator):
    """ObjectIterator that works on top of an ObjectStore."""

    def __init__(self, store, sha_iter):
        """Create a new ObjectIterator.

        :param store: Object store to retrieve from
        :param sha_iter: Iterator over (sha, path) tuples
        """
        self.store = store
        self.sha_iter = sha_iter
        self._shas = []

    def __iter__(self):
        """Yield tuple with next object and path."""
        for sha, path in self.itershas():
            yield self.store[sha], path

    def iterobjects(self):
        """Iterate over just the objects."""
        for o, path in self:
            yield o

    def itershas(self):
        """Iterate over the SHAs."""
        for sha in self._shas:
            yield sha
        for sha in self.sha_iter:
            self._shas.append(sha)
            yield sha

    def __contains__(self, needle):
        """Check if an object is present.

        :note: This checks if the object is present in
            the underlying object store, not if it would
            be yielded by the iterator.

        :param needle: SHA1 of the object to check for
        """
        return needle in self.store

    def __getitem__(self, key):
        """Find an object by SHA1.

        :note: This retrieves the object from the underlying
            object store. It will also succeed if the object would
            not be returned by the iterator.
        """
        return self.store[key]

    def __len__(self):
        """Return the number of objects."""
        return len(list(self.itershas()))


def tree_lookup_path(lookup_obj, root_sha, path):
    """Look up an object in a Git tree.

    :param lookup_obj: Callback for retrieving object by SHA1
    :param root_sha: SHA1 of the root tree
    :param path: Path to lookup
    :return: A tuple of (mode, SHA) of the resulting path.
    """
    tree = lookup_obj(root_sha)
    if not isinstance(tree, Tree):
        raise NotTreeError(root_sha)
    return tree.lookup_path(lookup_obj, path)


def _collect_filetree_revs(obj_store, tree_sha, kset):
    """Collect SHA1s of files and directories for specified tree.

    :param obj_store: Object store to get objects by SHA from
    :param tree_sha: tree reference to walk
    :param kset: set to fill with references to files and directories
    """
    filetree = obj_store[tree_sha]
    for name, mode, sha in filetree.iteritems():
        if not S_ISGITLINK(mode) and sha not in kset:
            kset.add(sha)
            if stat.S_ISDIR(mode):
                _collect_filetree_revs(obj_store, sha, kset)


def _split_commits_and_tags(obj_store, lst, ignore_unknown=False):
    """Split object id list into three lists with commit, tag, and other SHAs.

    Commits referenced by tags are included into commits
    list as well. Only SHA1s known in this repository will get
    through, and unless ignore_unknown argument is True, KeyError
    is thrown for SHA1 missing in the repository

    :param obj_store: Object store to get objects by SHA1 from
    :param lst: Collection of commit and tag SHAs
    :param ignore_unknown: True to skip SHA1 missing in the repository
        silently.
    :return: A tuple of (commits, tags, others) SHA1s
    """
    commits = set()
    tags = set()
    others = set()
    for e in lst:
        try:
            o = obj_store[e]
        except KeyError:
            if not ignore_unknown:
                raise
        else:
            if isinstance(o, Commit):
                commits.add(e)
            elif isinstance(o, Tag):
                tags.add(e)
                tagged = o.object[1]
                c, t, o = _split_commits_and_tags(
                    obj_store, [tagged], ignore_unknown=ignore_unknown)
                commits |= c
                tags |= t
                others |= o
            else:
                others.add(e)
    return (commits, tags, others)


class MissingObjectFinder(object):
    """Find the objects missing from another object store.

    :param object_store: Object store containing at least all objects to be
        sent
    :param haves: SHA1s of commits not to send (already present in target)
    :param wants: SHA1s of commits to send
    :param progress: Optional function to report progress to.
    :param get_tagged: Function that returns a dict of pointed-to sha -> tag
        sha for including tags.
    :param get_parents: Optional function for getting the parents of a commit.
    :param tagged: dict of pointed-to sha -> tag sha for including tags
    """

    def __init__(self, object_store, haves, wants, progress=None,
                 get_tagged=None, get_parents=lambda commit: commit.parents):
        self.object_store = object_store
        self._get_parents = get_parents
        # process Commits and Tags differently
        # Note, while haves may list commits/tags not available locally,
        # and such SHAs would get filtered out by _split_commits_and_tags,
        # wants shall list only known SHAs, and otherwise
        # _split_commits_and_tags fails with KeyError
        have_commits, have_tags, have_others = (
            _split_commits_and_tags(object_store, haves, True))
        want_commits, want_tags, want_others = (
            _split_commits_and_tags(object_store, wants, False))
        # all_ancestors is a set of commits that shall not be sent
        # (complete repository up to 'haves')
        all_ancestors = object_store._collect_ancestors(
            have_commits, get_parents=self._get_parents)[0]
        # all_missing - complete set of commits between haves and wants
        # common - commits from all_ancestors we hit into while
        # traversing parent hierarchy of wants
        missing_commits, common_commits = object_store._collect_ancestors(
            want_commits, all_ancestors, get_parents=self._get_parents)
        self.sha_done = set()
        # Now, fill sha_done with commits and revisions of
        # files and directories known to be both locally
        # and on target. Thus these commits and files
        # won't get selected for fetch
        for h in common_commits:
            self.sha_done.add(h)
            cmt = object_store[h]
            _collect_filetree_revs(object_store, cmt.tree, self.sha_done)
        # record tags we have as visited, too
        for t in have_tags:
            self.sha_done.add(t)

        missing_tags = want_tags.difference(have_tags)
        missing_others = want_others.difference(have_others)
        # in fact, what we 'want' is commits, tags, and others
        # we've found missing
        wants = missing_commits.union(missing_tags)
        wants = wants.union(missing_others)

        self.objects_to_send = set([(w, None, False) for w in wants])

        if progress is None:
            self.progress = lambda x: None
        else:
            self.progress = progress
        self._tagged = get_tagged and get_tagged() or {}

    def add_todo(self, entries):
        self.objects_to_send.update([e for e in entries
                                     if not e[0] in self.sha_done])

    def next(self):
        while True:
            if not self.objects_to_send:
                return None
            (sha, name, leaf) = self.objects_to_send.pop()
            if sha not in self.sha_done:
                break
        if not leaf:
            o = self.object_store[sha]
            if isinstance(o, Commit):
                self.add_todo([(o.tree, "", False)])
            elif isinstance(o, Tree):
                self.add_todo([(s, n, not stat.S_ISDIR(m))
                               for n, m, s in o.iteritems()
                               if not S_ISGITLINK(m)])
            elif isinstance(o, Tag):
                self.add_todo([(o.object[1], None, False)])
        if sha in self._tagged:
            self.add_todo([(self._tagged[sha], None, True)])
        self.sha_done.add(sha)
        self.progress(("counting objects: %d\r" %
                       len(self.sha_done)).encode('ascii'))
        return (sha, name)

    __next__ = next
