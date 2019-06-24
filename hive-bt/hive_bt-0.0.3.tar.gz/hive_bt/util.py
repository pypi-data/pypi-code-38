# This file is part of hive, a distributed bug tracker
# Copyright (c) 2019 by Adam Hartz <hz@mit.edu>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Utilities that don't belong anywhere else.
"""

import os
import shlex
import shutil
import tempfile
import textwrap
import subprocess

from datetime import datetime


def find_editor():
    if "EDITOR" in os.environ:
        return shlex.split(os.environ["EDITOR"])

    for cmd in ("editor", "vim", "emacs", "nano", "vi"):
        ed = shutil.which(cmd)
        if ed:
            return [ed]

    return None


def get_editor_markdown(initial_md="", quoted_md=""):
    editor = find_editor()
    if editor is None:
        raise FileNotFoundError("could not find a valid editor.  Please set $EDITOR.")

    with tempfile.NamedTemporaryFile(mode="r+", suffix=".md") as f:
        print(initial_md, file=f)
        print(file=f)
        print("--", file=f)
        print(
            textwrap.fill(
                quoted_md.replace("--", ""), initial_indent="> ", subsequent_indent="> "
            )
        )
        print(
            "Enter Markdown above the `--`.  Text below the last `--` will be ignored.",
            file=f,
        )
        f.flush()

        subprocess.check_call(editor + [f.name])

        f.seek(0)
        body = f.read()

    return body


def make_trie(word_list):
    top = {"value": None, "children": {}}
    for word in word_list:
        node = top
        for char in word:
            if char not in node["children"]:
                node["children"][char] = {"value": 1, "children": {}}
            else:
                node["children"][char]["value"] += 1
            node = node["children"][char]
    return top


def unique_prefixes(word_list):
    trie = make_trie(word_list)
    out = {}
    for word in word_list:
        node = trie
        prefix = ""
        ix = 0
        while node["value"] != 1:
            prefix += word[ix]
            node = node["children"][word[ix]]
            ix += 1
        out[word] = prefix
    return out


def format_time(t):
    return datetime.fromtimestamp(t).strftime("%d %b %Y; %I:%M %p")


def color_256(hex_):
    r = int(hex_[:2], 16)
    g = int(hex_[2:4], 16)
    b = int(hex_[4:6], 16)
    return 16 + round(r / 51) * 36 + round(g / 51) * 6 + round(b / 51)
