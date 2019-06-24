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
Python implementations of interactions with hive repositories.
"""

import hashlib

from . import data
from . import vcs

initialize = data.initialize


def new_issue(repo_root, author, title, body, parameters):
    parameters.update({"title": title, "body": body, "author": author})

    suffix = hashlib.md5(data.json_format(parameters).encode("utf-8")).hexdigest()
    new_id = None
    while new_id is None or new_id in data.list_issues(repo_root):
        new_id = data.new_issue_id(suffix)

    data.create_issue(repo_root, new_id)

    act = {"action": "set_parameters", "parameters": parameters}
    return new_id, data.add_action(repo_root, new_id, act)


def close_issue(repo_root, author, issue_id):
    return data.add_action(repo_root, issue_id, {"action": "close", "author": author})


def open_issue(repo_root, author, issue_id):
    return data.add_action(repo_root, issue_id, {"action": "open", "author": author})


def add_labels(repo_root, author, issue_id, labels):
    return data.add_action(
        repo_root, issue_id, {"action": "add_labels", "labels": set(labels)}
    )


def remove_labels(repo_root, author, issue_id, labels):
    return data.add_action(
        repo_root, issue_id, {"action": "remove_labels", "labels": set(labels)}
    )


def add_assignees(repo_root, author, issue_id, assignees):
    return data.add_action(
        repo_root, issue_id, {"action": "add_assignees", "assignees": set(assignees)}
    )


def remove_assignees(repo_root, author, issue_id, assignees):
    return data.add_action(
        repo_root, issue_id, {"action": "remove_assignees", "assignees": set(assignees)}
    )


def set_target(repo_root, author, issue_id, target):
    return data.add_action(
        repo_root,
        issue_id,
        {
            "action": "set_parameters",
            "author": author,
            "parameters": {"target": target},
        },
    )


def set_priority(repo_root, author, issue_id, priority):
    return data.add_action(
        repo_root,
        issue_id,
        {
            "action": "set_parameters",
            "author": author,
            "parameters": {"priority": priority},
        },
    )


def add_comment(repo_root, author, issue_id, body, parent=None):
    return data.add_action(
        repo_root,
        issue_id,
        {"action": "add_comment", "author": author, "body": body, "parent": parent},
    )


def edit_comment(repo_root, author, issue_id, comment_id, body):
    return data.add_action(
        repo_root,
        issue_id,
        {"action": "edit_comment", "author": author, "id": comment_id, "body": body},
    )


edit_label = data.edit_label
edit_target = data.edit_target
