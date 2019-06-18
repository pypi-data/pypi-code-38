"""

"""


import traceback as tb

from os.path import exists
import re


class OMP:
    def __init__(self):
        self._tree = None
        self._list = None
        return

    def loads(self, text, path=None):
        node_list = []
        lines = text.split("\n")
        min_lvl = 1
        cur_lvl = min_lvl
        indent_rx = re.compile(r"^(\*+)\s(.+)")
        level = None

        for idx, l in enumerate(lines):
            l = l.strip()
            match = indent_rx.match(l)
            if not match:
                continue
            level = match.group(1).count("*")
            head = match.group(2)
            node_list.append(
                {
                    "level": level,
                    "head": head,
                    "body": [],
                    "lineno": idx + 1,
                    "col_offset": level,
                }
            )
        self._list = node_list
        node_tree = self._make_tree(node_list, min_lvl)
        if path:
            node_tree = self.extract_path(node_tree, path)
        self._tree = node_tree
        return node_tree

    def _make_tree(self, node_list, level=1):
        cur_lvl = level
        tree = []
        sub_tree = []

        for node in node_list:

            if node["level"] == cur_lvl:

                if sub_tree:
                    # recurse to connect deeper nodes
                    tree[-1]["body"] = self._make_tree(sub_tree, cur_lvl + 1)
                    sub_tree = []
                tree.append(node)

            elif node["level"] > cur_lvl:
                # build sublist
                sub_tree.append(node)

            else:
                # TODO: handle level-less text nodes
                continue

        if sub_tree:
            # end of file with no next parent-sibling
            tree[-1]["body"] = self._make_tree(sub_tree, cur_lvl + 1)
        return tree

    def load(self, path):
        if not exists(path):
            raise OSError(f"{path} not found")
        retval = None

        with open(path) as fo:
            text = fo.read()
            self._text = text
            retval = self.loads(text)
        self._tree = retval
        return retval

    def dumps(self):
        return

    def dump(self):
        return

    def apply(self, func, *args, **kwds):
        if not callable(func):
            raise ValueError("Applicator must be a callable")
        return func(self, *args, **kwds)

    @property
    def tree(self):
        return self._tree

    def extract_path(self, nt, path):
        st = nt  # sub tree

        while path:
            sp = path.pop(0)  # sub path
            sp = int(sp) if str(sp).isdigit() else re.compile(sp)

            if isinstance(sp, int):
                if 1 > sp >= len(st):
                    raise ValueError(
                        f"Length of subtree is {len(st)} but got associated subpath of {sp}"
                    )
                st = st[sp - 1]

            else:
                for node in st:
                    if sp.match(node.get("head", "")):
                        st = node.get("body")
                        break
        if not isinstance(st, list):
            st = [st]
        return st
