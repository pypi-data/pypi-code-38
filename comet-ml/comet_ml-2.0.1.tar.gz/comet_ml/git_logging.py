# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
This module contains git related functions

"""

import logging
import os
import os.path
import sys
from io import BytesIO

import dulwich.errors
import dulwich.objects
import dulwich.patch
import dulwich.porcelain
import dulwich.repo
from six.moves.urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)

EMPTY_BLOB = dulwich.objects.Blob.from_string(b"")


def _patched_path_to_tree_path(repopath, path):
    """Convert a path to a path usable in e.g. an index.
    :param repopath: Repository
    :param path: A path
    :return: A path formatted for use in e.g. an index
    """
    if os.path.isabs(path):
        path = os.path.relpath(path, repopath)
    if os.path.sep != "/":
        path = path.replace(os.path.sep, "/")
    return path.encode(sys.getfilesystemencoding())


def to_utf8(str_or_bytes):
    if hasattr(str_or_bytes, "decode"):
        return str_or_bytes.decode("utf-8", errors="replace")

    return str_or_bytes


def get_user(repo):
    """ Retrieve the configured user from a dulwich git repository
    """
    try:
        # The user name might not be valid UTF-8
        return to_utf8(repo.get_config_stack().get("user", "name"))

    except KeyError:
        return None


def get_root(repo):
    """ Retrieve the hash of the repo root to uniquely identify the git
    repository
    """

    # Check if the repository is empty
    if len(repo.get_refs()) == 0:
        return None

    # Get walker needs at least the HEAD ref to be present
    walker = repo.get_walker()

    entry = None

    # Iterate on the lazy iterator to get to the last one
    for entry in walker:
        pass

    assert entry is not None

    # SHA should always be valid utf-8
    return to_utf8(entry.commit.id)


def get_branch(repo):
    """ Retrieve the current branch of a dulwich repository
    """
    refnames, sha = repo.refs.follow(b"HEAD")

    if len(refnames) != 2:
        LOGGER.debug("Got more than two refnames for HEAD!")

    for ref in refnames:
        if ref != b"HEAD":
            return to_utf8(ref)


def get_git_commit(repo):
    try:
        # SHA should always be valid utf-8
        return to_utf8(repo.head())

    except KeyError:
        return None


def git_status(repo):
    try:
        # Monkey-patch a dulwich method, see
        # https://github.com/dulwich/dulwich/pull/601 for an explanation why
        original = dulwich.porcelain.path_to_tree_path
        dulwich.porcelain.path_to_tree_path = _patched_path_to_tree_path

        status = dulwich.porcelain.status(repo)

        staged = {
            key: [to_utf8(path) for path in items]
            for (key, items) in status.staged.items()
        }
        unstaged = [to_utf8(path) for path in status.unstaged]
        untracked = [to_utf8(path) for path in status.untracked]

        return {"staged": staged, "unstaged": unstaged, "untracked": untracked}

    finally:
        dulwich.porcelain.path_to_tree_path = original


def get_origin_url(repo):
    repo_config = repo.get_config()
    try:
        # The origin url might not be valid UTF-8
        return to_utf8(repo_config.get((b"remote", b"origin"), "url"))

    except KeyError:
        return None


def get_repo_name(origin_url):
    if origin_url is None:
        return None

    # First parse the url to get rid of possible HTTP comments or arguments
    parsed_url = urlparse(origin_url)
    # Remove potential leading /
    path = parsed_url.path.rstrip("/")
    repo_name = path.split("/")[-1]

    # Remove potential leading .git
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return repo_name


def patched_gen_diff_header(paths, modes, shas):
    """Write a blob diff header.

    :param paths: Tuple with old and new path
    :param modes: Tuple with old and new modes
    :param shas: Tuple with old and new shas

    PATCHED: see https://github.com/dulwich/dulwich/issues/642 for explanation
    Also fix path support as patch are not cleaned anymore
    """
    (old_path, new_path) = paths
    (old_mode, new_mode) = modes
    (old_sha, new_sha) = shas
    shortid = dulwich.patch.shortid
    if old_path is None and new_path is not None:
        old_path = new_path
    if new_path is None and old_path is not None:
        new_path = old_path
    old_path = dulwich.patch.patch_filename(old_path, b"a")
    new_path = dulwich.patch.patch_filename(new_path, b"b")
    yield b"diff --git " + old_path + b" " + new_path + b"\n"

    if old_mode != new_mode:
        if new_mode is not None:
            if old_mode is not None:
                yield ("old file mode %o\n" % old_mode).encode("ascii")

            yield ("new file mode %o\n" % new_mode).encode("ascii")

        else:
            yield ("deleted file mode %o\n" % old_mode).encode("ascii")

    yield b"index " + shortid(old_sha) + b".." + shortid(new_sha)

    if new_mode is not None and old_mode is not None:
        yield (" %o" % new_mode).encode("ascii")

    yield b"\n"


def patched_write_object_diff(f, store, old_file, new_file, diff_binary=False):
    """Write the diff for an object.

    :param f: File-like object to write to
    :param store: Store to retrieve objects from, if necessary
    :param old_file: (path, mode, hexsha) tuple
    :param new_file: (path, mode, hexsha) tuple
    :param diff_binary: Whether to diff files even if they
        are considered binary files by is_binary().

    :note: the tuple elements should be None for nonexistant files

    PATCHED: Don't use /dev/null in header to respect Git format
    """
    (old_path, old_mode, old_id) = old_file
    (new_path, new_mode, new_id) = new_file
    patched_old_path = dulwich.patch.patch_filename(old_path, b"a")
    patched_new_path = dulwich.patch.patch_filename(new_path, b"b")

    def content(mode, hexsha):
        if hexsha is None:
            return dulwich.objects.Blob.from_string(b"")
        elif dulwich.objects.S_ISGITLINK(mode):
            return dulwich.objects.Blob.from_string(
                b"Subproject commit " + hexsha + b"\n"
            )
        else:
            return store[hexsha]

    def lines(content):
        if not content:
            return []
        else:
            return content.splitlines()

    f.writelines(
        patched_gen_diff_header(
            (old_path, new_path), (old_mode, new_mode), (old_id, new_id)
        )
    )
    old_content = content(old_mode, old_id)
    new_content = content(new_mode, new_id)
    if not diff_binary and (
        dulwich.patch.is_binary(old_content.data)
        or dulwich.patch.is_binary(new_content.data)
    ):
        f.write(
            b"Binary files "
            + patched_old_path
            + b" and "
            + patched_new_path
            + b" differ\n"
        )
    else:
        f.writelines(
            dulwich.patch.unified_diff(
                lines(old_content),
                lines(new_content),
                patched_old_path,
                patched_new_path,
            )
        )


class OverrideObjectStore(object):
    def __init__(self, repo_object_store):
        self.repo_object_store = repo_object_store
        self.override = {}

    def __getitem__(self, sha):
        blob = self.override.get(sha)

        if blob is None:
            blob = self.repo_object_store[sha]

        return blob

    def __setitem__(self, sha, blob):
        self.override[sha] = blob


def get_git_patch(repo, unstaged=True):
    final_changes = {}
    store = OverrideObjectStore(repo.object_store)

    try:
        head = repo.head()
    except KeyError:
        return None

    tree_id = repo[head].tree
    tree = repo[tree_id]

    index = repo.open_index()

    normalizer = repo.get_blob_normalizer()
    filter_callback = normalizer.checkin_normalize
    object_store = repo.object_store
    blob_from_path_and_stat = dulwich.index.blob_from_path_and_stat
    cleanup_mode = dulwich.index.cleanup_mode
    lookup_path = tree.lookup_path
    repo_path = repo.path.encode(sys.getfilesystemencoding())

    def lookup_entry(path):
        absolute_path = os.path.join(repo_path, path)
        if os.path.isfile(absolute_path):
            st = os.lstat(absolute_path)
            # TODO: Building the blob means that we need to load the whole
            # file content in memory. We should be able to compute the sha
            # without needed to load the whole blob in memory.
            blob = blob_from_path_and_stat(absolute_path, st)
            blob = filter_callback(blob, path)
            blob_id = blob.id

            mode = cleanup_mode(st.st_mode)

            # Check if on-disk blob differs from the one in tree
            try:
                tree_blob = lookup_path(object_store.__getitem__, path)
            except KeyError:
                # Lookup path will fails for added files
                store[blob_id] = blob
            else:
                # If the blob for path in index differs from the one on disk,
                # store the on-disk one
                if tree_blob[1] != blob_id:
                    store[blob_id] = blob

            return blob_id, mode
        elif os.path.isdir(absolute_path):
            try:
                tree_blob = lookup_path(object_store.__getitem__, path)
            except KeyError:
                # If the submodule is not in the store, it must be in index
                # and should be added
                index_entry = index[path]
                return index_entry.sha, index_entry.mode

            tree_mode = tree_blob[0]

            if dulwich.objects.S_ISGITLINK(tree_mode):
                return tree_blob[1], tree_mode
            else:
                # We shouldn't be here?
                raise KeyError(path)
        else:
            # Indicate that the files has been removed
            raise KeyError(path)

    # Merges names from the index and from the store as some files can be only
    # on index or only on the store
    names = set()
    for (name, _, _) in object_store.iter_tree_contents(tree_id):
        names.add(name)

    names.update(index._byname.keys())

    final_changes = dulwich.index.changes_from_tree(
        names, lookup_entry, repo.object_store, tree_id, want_unchanged=False
    )

    # Generate the diff

    diff = BytesIO()

    def key(x):
        # Generate a comparable sorting key
        paths = tuple(p for p in x[0] if p)
        return paths

    for (oldpath, newpath), (oldmode, newmode), (oldsha, newsha) in sorted(
        final_changes, key=key
    ):
        patched_write_object_diff(
            diff, store, (oldpath, oldmode, oldsha), (newpath, newmode, newsha)
        )

    diff.seek(0)
    diff_result = diff.getvalue()

    # Detect empty diff
    if not diff_result:
        return None

    return diff_result


def find_git_patch(path):
    # First find the repo
    repo = find_git_repo(path)

    if not repo:
        return None

    patch = get_git_patch(repo)

    # Close the repo to close all opened fds
    repo.close()

    return patch


def find_git_repo(repo_path):
    # Early-exit if repo_path is repo root
    try:
        return dulwich.repo.Repo(repo_path)

    except dulwich.errors.NotGitRepository:
        pass

    path = repo_path
    while path:
        parent_path = os.path.dirname(path)
        # Avoid infinite loop
        if parent_path == path:
            break

        path = parent_path
        try:
            return dulwich.repo.Repo(path)

        except dulwich.errors.NotGitRepository:
            pass


def get_git_metadata(path):
    # First find the repo
    repo = find_git_repo(path)

    if not repo:
        return None

    origin = get_origin_url(repo)
    repo_name = get_repo_name(origin)

    data = {
        "user": get_user(repo),
        "root": get_root(repo),
        "branch": get_branch(repo),
        "parent": get_git_commit(repo),
        "status": None,
        "origin": origin,
        "repo_name": repo_name,
    }

    # Close the repo to close all opened fds
    repo.close()

    return data
