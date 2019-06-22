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
Functions for working with hive's data format (getting information about an
issue, etc).
"""

import os
import ast
import sys
import json
import time
import pickle
import hashlib
import contextlib

import tqdm

from uuid import uuid4
from datetime import datetime

DATA_VERSION = 1


class HiveDataException(Exception):
    pass


def json_dump(x, f):
    return json.dump(
        x,
        f,
        sort_keys=True,
        indent=2,
        default=lambda x: list(x) if isinstance(x, set) else None,
    )


def json_format(x):
    return json.dumps(
        x,
        sort_keys=True,
        indent=2,
        default=lambda x: list(x) if isinstance(x, set) else None,
    )


def initialize(repo_root):
    """
    set up hive's initial structure in repo_root/.hive-bt
    """
    hive_root = os.path.join(repo_root, ".hive-bt")
    if os.path.exists(hive_root):
        raise HiveDataException("hive repository already exists at %s" % hive_root)

    os.makedirs(hive_root, exist_ok=True)
    with open(os.path.join(hive_root, "version"), "w") as f:
        f.write("hive-%d\n" % DATA_VERSION)

    for subdir in ("issues", "labels", "targets"):
        os.makedirs(os.path.join(hive_root, subdir))
        with open(os.path.join(hive_root, subdir, ".keep"), "w") as f:
            pass


def get_issue_location(repo_root, issue_id):
    hive_root = os.path.join(repo_root, ".hive-bt")
    if not os.path.isdir(hive_root):
        raise HiveDataException("No hive repository here.")
    issue_id = issue_id.lower()
    possible_issues = [i for i in list_issues(repo_root) if i.startswith(issue_id)]
    if not possible_issues:
        raise HiveDataException("No bug with ID %s" % issue_id)
    elif len(possible_issues) > 2:
        raise HiveDataException(
            "Ambiguous issue ID %r (possibilities: %r)" % (issue_id, possible_issues)
        )
    issue_id = possible_issues[0]
    return issue_id, os.path.join(hive_root, "issues", issue_id)


def real_comment_id(repo_root, issue_id, comment_prefix):
    all_ids = set(get_issue_state(repo_root, issue_id)["comments_by_id"])
    possible = [i for i in all_ids if i.startswith(comment_prefix)]
    if not possible:
        raise HiveDataException("No comment with ID %s" % comment_prefix)
    elif len(possible) > 2:
        raise HiveDataException(
            "Ambiguous comment ID %r (possibilities: %r)" % (comment_prefix, possible)
        )
    return possible[0]


def list_issues(repo_root):
    hive_root = os.path.join(repo_root, ".hive-bt", "issues")
    if not os.path.isdir(hive_root):
        raise HiveDataException("No hive repository here.")
    return set(os.listdir(hive_root)) - {".keep"}


def new_issue_id(suffix):
    return "%s%s" % (uuid4().hex, suffix)


def issue_exists(repo_root, issue_id):
    return os.path.isdir(os.path.join(repo_root, ".hive-bt", "issues", issue_id))


def create_issue(repo_root, issue_id):
    try:
        os.makedirs(os.path.join(repo_root, ".hive-bt", "issues", issue_id))
    except Exception as e:
        raise HiveDataException("Could not create issue %r" % issue_id) from e


def next_logical_time(repo_root):
    hive_root = os.path.join(repo_root, ".hive-bt")
    if not os.path.isdir(hive_root):
        raise HiveDataException("Not within a hive repository.")
    issues_root = os.path.join(hive_root, "issues")
    best = -1
    for root, dirs, files in os.walk(issues_root):
        files = [f for f in files if not f.startswith(".")]
        best = max(max(int(f.split("-")[0]) for f in files) if files else -1, best)
    return best + 1


def valid_label_name(x, type_="label"):
    invalid_chars = r"\/ :."
    if not (x and all(i not in x for i in invalid_chars)):
        raise HiveDataException("invalid %s name: %r" % (type_, x))


def edit_label(repo_root, label_name, description):
    valid_label_name(label_name)
    with open(os.path.join(repo_root, ".hive-bt", "labels", label_name), "w") as f:
        json_dump(description, f)
    return label_name


def label_information(repo_root):
    label_root = os.path.join(repo_root, ".hive-bt", "labels")
    out = {}
    for i in os.listdir(label_root):
        try:
            valid_label_name(i)
        except HiveDataException:
            continue
        with open(os.path.join(label_root, i), "r") as f:
            out[i] = json.load(f)
    return out


def edit_target(repo_root, target_name, description):
    valid_target_name(target_name, type_="target")
    with open(os.path.join(repo_root, ".hive-bt", "targets", target_name), "w") as f:
        json_dump(description, f)
    return target_name


def add_action(repo_root, issue_id, action, exact=False):
    if exact:
        issue_dir = os.path.join(repo_root, ".hive-bt", "issues", issue_id)
    else:
        issue_id, issue_dir = get_issue_location(repo_root, issue_id)
    action_id = "%d-%d-%s" % (
        next_logical_time(repo_root),
        time.time() * 1000,
        hashlib.md5(json_format(action).encode("utf-8")).hexdigest(),
    )
    action["id"] = action_id
    with open(os.path.join(issue_dir, action_id), "w") as f:
        json_dump([action], f)
    return action_id


def _time_from_id(i):
    pieces = i.split("-")
    return int(pieces[0]), int(pieces[1])


def pack(repo_root, issue_id, files):
    if not files:
        raise HiveDataException("no action files specified")
    issue_root = os.path.join(repo_root, ".hive-bt", "issues", issue_id)
    if files == "all":
        files = os.listdir(issue_root)
    if len(files) == 1:
        raise HiveDataException("only one file specified; already packed!")
    files = [os.path.join(issue_root, fname) for fname in files]
    for f in files:
        if not os.path.isfile(f):
            raise HiveDataException("no such action file: %s" % f)
    actions = []
    for fname in files:
        with open(os.path.join(issue_root, fname)) as f:
            actions.extend(json.load(f))
    if len(actions) <= 1:
        raise HiveDataException("only one action specified; not packing")
    actions.sort(key=lambda x: _time_from_id(x["id"]))
    pack_time = _time_from_id(actions[-1]["id"])
    pack_contents = json_format(actions)
    hash_ = hashlib.md5(pack_contents.encode("utf-8")).hexdigest()
    pack_fname = "%d-%d-%s" % (*pack_time, hash_)
    with open(os.path.join(issue_root, pack_fname), "w") as f:
        f.write(pack_contents)
    for fname in files:
        if fname != pack_fname:
            os.unlink(os.path.join(issue_root, fname))
    return pack_fname, len(actions)


def unpack(repo_root, issue_id, fname):
    issue_root = os.path.join(repo_root, ".hive-bt", "issues", issue_id)
    fname = os.path.join(issue_root, fname)
    with open(fname) as f:
        actions = json.load(f)
    if len(actions) <= 1:
        raise HiveDataException("only one action specified; nothing to unpack")
    ids = []
    for action in actions:
        with open(os.path.join(issue_root, action["id"]), "w") as f:
            json_dump([action], f)
        ids.append(action["id"])
    os.unlink(fname)
    return ids, len(actions)


def get_cache_location():
    home_dir = os.path.expanduser("~")
    if "XDG_CACHE_HOME" in os.environ:
        return os.environ["XDG_CACHE_HOME"]
    elif sys.platform.startswith("darwin"):
        return os.path.join(home_dir, "Library", "Caches", "hive_bt")
    elif sys.platform.startswith("win32"):
        return os.path.join(os.environ["LOCALAPPDATA"], "hive_bt")
    else:
        return os.path.join(home_dir, ".cache", "hive_bt")


def _splitpath(path, sofar=[]):
    folder, path = os.path.split(path)
    if path == "":
        return sofar[::-1]
    elif folder == "":
        return (sofar + [path])[::-1]
    else:
        return _splitpath(folder, sofar + [path])


def get_issue_state(repo_root, issue_id, time=None, exact=False):
    if exact:
        issue_dir = os.path.join(repo_root, ".hive-bt", "issues", issue_id)
    else:
        orig_id = issue_id
        issue_id, issue_dir = get_issue_location(repo_root, issue_id)
        if not issue_id:
            raise HiveDataException("No such issue: %r" % orig_id)
    info = {
        "id": issue_id,
        "updated_times": [],
        "labels": set(),
        "assignees": set(),
        "priority": 0,
        "target": None,
        "open": True,
        "comments": [],
    }
    comments_by_id = {}
    info["comments_by_id"] = comments_by_id
    actions = []
    for filename in os.listdir(issue_dir):
        with open(os.path.join(issue_dir, filename)) as f:
            this_pack_actions = json.load(f)
        for action in this_pack_actions:
            pieces = action["id"].split("-")
            actions.append(
                (int(pieces[0]), int(pieces[1]), pieces[2], action["id"], action)
            )
    actions.sort()
    for logicaltime, unixtime, hash_, action_id, action in actions:
        if time is not None and logicaltime > time:
            break
        unixtime /= 1000
        action_name = action["action"]
        info["labels"] = set(info["labels"])

        # decide how to update the state based on the given action
        if action_name == "set_parameters":
            info.update(action["parameters"])
            info["labels"] = set(info["labels"])

        elif action_name == "add_labels":
            info["labels"] = set(info["labels"]) | set(action["labels"])

        elif action_name == "remove_labels":
            info["labels"] = set(info["labels"]) - set(action["labels"])

        elif action_name == "add_assignees":
            info["assignees"] = set(info["assignees"]) | set(action["assignees"])

        elif action_name == "remove_assignees":
            info["assignees"] = set(info["assignees"]) - set(action["assignees"])

        elif action_name == "open":
            info["open"] = True
        elif action_name == "close":
            info["open"] = False

        elif action_name == "add_comment":
            comment = comments_by_id[action_id] = {
                k: v
                for k, v in action.items()
                if k not in {"action", "parent", "author"}
            }
            comment["authors"] = [action["author"]]
            comment["edited"] = False
            comment["id"] = action_id
            comment["display_time"] = unixtime

            parent = action.get("parent", None)
            if parent in comments_by_id:
                comments_by_id[parent].setdefault("children", []).append(comment)
            else:
                info["comments"].append(comment)
        elif action_name == "edit_comment":
            comments_by_id[action["id"]].update(
                {
                    k: v
                    for k, v in action.items()
                    if k not in {"action", "parent", "author"}
                }
            )
            comments_by_id[action["id"]]["authors"].append(action["author"])
            comments_by_id[action["id"]]["edited"] = True

        # update timestamps
        info["updated_times"].append((logicaltime, unixtime))

    return info


sort_funcs = {
    "priority": (lambda x: x.get("priority", 0) or 0, True),
    "created_time": (lambda x: x["updated_times"][0], True),
    "updated_time": (lambda x: x["updated_times"][-1], True),
    "title": (lambda x: x["title"].lower(), False),
    "status": (lambda x: 1 if x["open"] else -1, True),
}


def _any_filter(i, q):
    return any(
        filter_funcs[filt](i, q) for filt in ("body", "title", "author", "label")
    )


filter_funcs = {
    "priority>": lambda i, q: sort_funcs["priority"](i) > ast.literal_eval(q),
    "priority<": lambda i, q: sort_funcs["priority"](i) < ast.literal_eval(q),
    "priority": lambda i, q: sort_funcs["priority"](i) == ast.literal_eval(q),
    "label": lambda i, q: q in i["labels"],
    "status": lambda i, q: True
    if q == "any"
    else i["open"]
    if q == "open"
    else not i["open"]
    if q == "closed"
    else False,
    "body": lambda i, q: q.lower() in i["body"].lower(),
    "title": lambda i, q: q.lower() in i["title"].lower(),
    "author": lambda i, q: q.lower() in i["author"].lower(),
    "id": lambda i, q: i["id"].lower().startswith(q.lower()),
    "any": _any_filter,
}


@contextlib.contextmanager
def atomic_write(fname, mode="w"):
    new_name = "%s.%s.part" % (fname, uuid4().hex)
    with open(new_name, mode) as f:
        yield f
        f.flush()
    os.replace(new_name, fname)


def cached_all_issues(repo_root, override_cache=False, progress=False):
    cache_dir = os.path.join(get_cache_location(), *_splitpath(repo_root), ".hive-bt")
    cache_loc = os.path.join(cache_dir, "issues.pickle")

    max_mtime = -float("inf")
    for root, dirs, files in os.walk(os.path.join(repo_root, ".hive-bt", "issues")):
        max_mtime = max(
            max_mtime,
            os.stat(root).st_mtime,
            max(os.stat(os.path.join(root, f)).st_mtime for f in files)
            if files
            else -1,
        )

    if (
        (not override_cache)
        and os.path.isfile(cache_loc)
        and os.stat(cache_loc).st_mtime > max_mtime
    ):
        try:
            with open(cache_loc, "rb") as f:
                return pickle.load(f)
        except:
            pass
    all_issues = []
    list_ = list_issues(repo_root)
    if progress:
        list_ = tqdm.tqdm(list_)
    for issue in list_:
        all_issues.append(get_issue_state(repo_root, issue, exact=True))
    os.makedirs(cache_dir, exist_ok=True)
    with atomic_write(cache_loc, "wb") as f:
        pickle.dump(all_issues, f, pickle.HIGHEST_PROTOCOL)
    return all_issues


def all_issues_state(
    repo_root, sorts=None, reverse_sort=False, filters=None, include_closed=False
):
    all_issues = cached_all_issues(repo_root)
    filters = list(filters or [])
    if not include_closed and "status" not in {i[0] for i in filters}:
        filters.append(("status", "open"))
    sorts = sorts or ["priority", "created_time"]
    for func, query in filters:
        try:
            all_issues = [
                issue for issue in all_issues if filter_funcs[func](issue, query)
            ]
        except KeyError:
            raise HiveDataException("No filter function called %r" % func)
    for func in reversed(sorts):
        try:
            func, reverse = sort_funcs[func]
            if reverse_sort:
                reverse = not reverse
            all_issues.sort(key=func, reverse=reverse)
        except KeyError:
            raise HiveDataException("No sorting function called %r" % func)
    return all_issues
