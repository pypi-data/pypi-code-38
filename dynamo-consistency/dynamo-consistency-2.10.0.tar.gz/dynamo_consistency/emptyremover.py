"""
Defines a class that can remove nodes from a :py:class:`DirectoryInfo` object
"""

import logging

from os.path import join

from . import datatypes
from . import history
from . import config
from .backend import registry


LOG = logging.getLogger(__name__)


class EmptyRemover(object):
    """
    This class handles the removal of empty directories from the tree
    by behaving as a callback.
    It also calls deletions for the registry at the same time.

    :param str site: Site name. If value is ``None``, then don't enter deletions
                     into the registry, but still remove node from tree
    :param function check: The function to check against orphans to not delete.
                           The full path name is passed to the function.
                           If it returns ``True``, the directory is not deleted.
    """

    def __init__(self, site, check=None):
        self.site = site
        self.check = check or (lambda _: False)
        self.removed = 0
        self.root = config.config_dict()['RootPath']
        # This is a set of directories that have a filtered directory inside
        self.not_empty = set()

    def fullname(self, name):
        """
        Get the full LFN of a path.
        Checkes if the root is included, and adds it if necessary.

        .. Note::
           Won't work if the root name is the same as a relative path inside it.

        :param str name: May be a relative path to the root
        :returns: Full LFN
        :rtype: str
        """

        return join(self.root, name) \
            if not name.startswith(self.root) else name

    def __call__(self, tree):
        """
        Removes acceptable empty directories from the tree

        :param tree: The tree that is periodically cleaned by this
        :type tree: :py:class:`datatypes.DirectoryInfo`
        """
        tree.setup_hash()
        empties = [empty for empty in tree.empty_nodes_list()
                   if not self.check(self.fullname(empty)) and
                   empty not in self.not_empty]

        LOG.debug('Sees %s', empties)

        strip_len = len(tree.name) + 1
        empties_info = []

        for path in empties:
            try:
                info = (
                    self.fullname(path),
                    tree.get_node(path[strip_len:], make_new=False).mtime
                    )
                tree.remove_node(path)
                empties_info.append(info)

            except datatypes.NotEmpty as msg:
                LOG.warning('While removing %s: %s', path, msg)
                self.not_empty.add(path)

        full_empties = [info[0] for info in empties_info]

        history.report_empty(empties_info)

        self.removed += registry.delete(self.site, full_empties) \
            if self.site and full_empties else len(full_empties)

    def get_removed_count(self):
        """
        :returns: The number of directories removed by this function object
        :rtype: int
        """
        return self.removed
