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
import json
import time
import hashlib

from uuid import uuid4
from datetime import datetime

DATA_VERSION = 0


class HiveDataException(Exception):
    pass


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
    hive_root = os.path.join(repo_root, ".hive-bt")
    if not os.path.isdir(hive_root):
        raise HiveDataException("No hive repository here.")
    return [
        i
        for i in os.listdir(os.path.join(hive_root, "issues"))
        if not i.startswith(".")
    ]


def new_issue_id():
    return uuid4().hex


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
        f.write(json_format(description))
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
        f.write(json_format(description))
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
    with open(os.path.join(issue_dir, action_id), "w") as f:
        f.write(json_format(action))
    return action_id


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
    possibilities = []
    for i in os.listdir(issue_dir):
        pieces = i.split("-")
        possibilities.append((int(pieces[0]), int(pieces[1]), pieces[2], i))
    for logicaltime, unixtime, hash_, action_id in sorted(possibilities):
        if time is not None and logicaltime > time:
            break
        unixtime /= 1000
        with open(os.path.join(issue_dir, action_id)) as f:
            action = json.loads(f.read())
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


def all_issues_state(
    repo_root, sorts=None, reverse_sort=False, filters=None, include_closed=False
):
    filters = list(filters or [])
    if not include_closed and "status" not in {i[0] for i in filters}:
        filters.append(("status", "open"))
    sorts = sorts or ["priority", "created_time"]
    all_issues = [get_issue_state(repo_root, issue) for issue in list_issues(repo_root)]
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
            all_issues = sorted(all_issues, key=func, reverse=reverse)
        except KeyError:
            raise HiveDataException("No sorting function called %r" % func)
    return all_issues
