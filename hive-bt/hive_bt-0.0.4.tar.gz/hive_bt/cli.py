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
Command-line Interface for hive
"""

import io
import os
import re
import sys
import click
import shutil
import textwrap
import termcolor
import webbrowser

from datetime import datetime

from . import vcs
from . import util
from . import data
from . import commands
from . import __version__

from .web import app


def colored(text, fgcolor=None, bgcolor=None, **kwargs):
    if not sys.stdout.isatty():
        return text
    elif fgcolor is not None and bgcolor is not None:
        return "\x1b[38;5;%d;48;5;%dm%s\x1b[0m" % (
            util.color_256(fgcolor),
            util.color_256(bgcolor),
            text,
        )
    return termcolor.colored(text, fgcolor, **kwargs)


def body_from_stdin_or_editor(stdin, initial_md="", quoted_md="", allow_empty=False):
    if stdin:
        body = sys.stdin.read()
    else:
        body = util.get_editor_markdown(initial_md=initial_md, quoted_md=quoted_md)
        body = body.split("--", 1)[0].strip()
        if (not body) and (not allow_empty):
            click.echo(colored("No body text supplied.", "red"), err=True)
            sys.exit(1)
        elif body == initial_md.strip():
            click.echo(colored("No change to body text.", "red"), err=True)
            sys.exit(1)
    return body


_alias_map = {"ls": "list", "tag": "label", "add": "new"}

# from http://click.palletsprojects.com/en/5.x/advanced/
class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        if cmd_name in _alias_map:
            cmd_name = _alias_map[cmd_name]
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail("Too many matches: %s" % ", ".join(sorted(matches)))


@click.command(cls=AliasedGroup)
def main():
    pass


def is_repo_helper(repo_root):
    hive_loc = os.path.join(repo_root, ".hive-bt")
    if not os.path.isdir(hive_loc):
        click.echo(
            colored(
                'ERROR: no hive repository at %s; run "hive init" to initialize it'
                % (hive_loc),
                "red",
            ),
            err=True,
        )
        sys.exit(1)


def find_repo_helper(error_on_no_identity=False, error_on_no_hive=True):
    repo_info = vcs.get_repo_info()
    if repo_info is None:
        click.echo(
            colored(
                "ERROR: hive must be run from within a Git or Mercurial repository",
                "red",
            ),
            err=True,
        )
        sys.exit(1)
    if error_on_no_hive and not os.path.isdir(
        os.path.join(repo_info["root"], ".hive-bt", "issues")
    ):
        click.echo(colored("ERROR: no hive issue repository here.", "red"))
        sys.exit(1)
    if repo_info["name"] is None:
        color = "red" if error_on_no_identity else "magenta"
        click.echo(
            colored("ERROR: identity not set in gitconfig or hgrc", color), err=True
        )
        if error_on_no_identity:
            sys.exit(1)
    return repo_info


@click.command()
@click.option(
    "-c",
    "--commit",
    is_flag=True,
    help="Flag to add the structure to the repository and commit.",
)
@click.option(
    "-m",
    "--message",
    default=None,
    help="If -c is specified, this message will be used as the commit message.  If not specified, a default message will be used.",
)
def init(commit, message):
    """
    Initialize a hive repository
    """
    repo_info = find_repo_helper(error_on_no_hive=False)
    try:
        commands.initialize(repo_info["root"])
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)
    click.echo(
        colored(
            "Initialized hive repository at %s"
            % os.path.join(repo_info["root"], ".hive-bt"),
            "green",
        )
    )
    if commit:
        msg = message or "Initialize hive repository in .hive-bt"
        vcs.add(repo_info)
        vcs.commit(repo_info, msg=msg)


def uline(x):
    return colored(x, attrs=["underline"])


def print_comment(c, indent="  | ", limit=80):
    print(indent + uline("Comment ID:"), c["id"])
    print(indent + uline("Author:"), c["authors"][0])
    print(indent + uline("Created:"), util.format_time(c["display_time"]))
    print(indent)
    print(
        textwrap.TextWrapper(
            break_long_words=False,
            initial_indent=indent,
            subsequent_indent=indent,
            width=limit,
        ).fill(c["body"])
    )
    print(indent)
    for child in c.get("children", []):
        print(indent)
        print(indent)
        print_comment(child, indent="%s  | " % indent, limit=limit)


@click.command()
@click.argument("issue")
def show(issue):
    """
    Display information about a particular issue
    """
    repo_info = find_repo_helper()
    try:
        issue = data.get_issue_state(repo_info["root"], issue)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)
    print(uline("Issue ID:"), issue["id"])
    print(uline("Title:"), issue["title"].strip())
    print(uline("Submitter:"), issue["author"])
    if issue.get("reporter", None) is not None:
        print(uline("Reporter:"), issue["reporter"])
    print(uline("Created:"), util.format_time(issue["updated_times"][0][1]))
    if len(issue["updated_times"]) > 1:
        print(uline("Last Updated:"), util.format_time(issue["updated_times"][-1][1]))
    print(uline("Priority:"), issue["priority"])
    print(
        uline("Labels:"),
        format_labels(
            sorted(issue["labels"]), data.label_information(repo_info["root"])
        ),
    )
    print(uline("Assignees:"), ", ".join(issue["assignees"]))
    print()
    print(
        textwrap.TextWrapper(
            break_long_words=False, width=shutil.get_terminal_size()[0]
        ).fill(issue["body"])
    )
    for comment in issue["comments"]:
        print()
        print()
        print_comment(comment, limit=shutil.get_terminal_size()[0])


@click.command(name="list")
@click.argument("search_term", nargs=-1)
@click.option(
    "-s",
    "--sort-by",
    multiple=True,
    help="Function to sort by.  Specifying multiple times will set secondary, tertiary, ..., sorts..",
    type=click.Choice(data.sort_funcs),
)
@click.option(
    "--long-ids",
    is_flag=True,
    help="Show full issue IDs, rather than minimally short IDs",
)
@click.option("-r", "--reverse-sort", is_flag=True, help="Sort in reverse order.")
@click.option(
    "--max-title-length", type=int, help="Maximum title length to show", default=50
)
@click.option("-a", "--all", is_flag=True, help="List all issues, not just open ones")
def list_(search_term, sort_by, long_ids, reverse_sort, max_title_length, all):
    """
    Show a summary of issues
    """
    repo_info = find_repo_helper()

    filters = []
    for i in search_term:
        i = i.lower()
        for filt in data.filter_funcs:
            if i.startswith("%s:" % filt):
                filters.append(tuple(i.split(":", 1)))
                break
        else:
            filters.append(("any", i))
    try:
        all_issues = data.all_issues_state(
            repo_info["root"],
            sorts=sort_by,
            filters=filters,
            reverse_sort=reverse_sort,
            include_closed=all,
        )
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    label_info = data.label_information(repo_info["root"])
    modified_issues = vcs.modified_issues(repo_info)

    if not all_issues:
        click.echo(colored("No matching issues", "red"))
        sys.exit(0)

    longest_title = 0
    longest_priority = 0
    longest_comments = 0
    for issue in all_issues:
        if len(issue["title"]) > max_title_length - 3:
            issue["title"] = "%s..." % (issue["title"][: max_title_length - 3],)
        issue["priority"] = "P%s" % issue["priority"]
        issue["comment_str"] = "%dc" % len(issue["comments_by_id"])
        issue["oid"] = issue["id"]
        longest_title = max(len(issue["title"]), longest_title)
        longest_priority = max(len(issue["priority"]), longest_priority)
        longest_comments = max(len(issue["comment_str"]), longest_comments)

    if not long_ids:
        prefixes = util.unique_prefixes(data.list_issues(repo_info["root"]))
        for issue in all_issues:
            issue["id"] = prefixes[issue["id"]]

    max_id_length = max(len(i["id"]) for i in all_issues)

    for issue in all_issues:
        print(
            colored(
                ("{0: >.%ds}" % max_id_length).format(
                    issue["id"].rjust(max_id_length, " ")
                ),
                "green" if issue["open"] else "red",
                attrs=["bold"],
            ),
            end="  ",
        )
        print(
            ("{0: <.%ds}" % longest_title).format(
                issue["title"].ljust(longest_title, " ")
            ),
            end="  ",
        )
        print(
            datetime.fromtimestamp(issue["updated_times"][0][1]).strftime(
                "%Y-%m-%d %H:%M"
            ),
            end="  ",
        )
        print(
            ("{0: <.%ds}" % longest_priority).format(
                issue["priority"].ljust(longest_priority, " ")
            ),
            end="  ",
        )
        print(
            ("{0: <.%ds}" % longest_comments).format(
                issue["comment_str"].rjust(longest_comments, " ")
            ),
            end="  ",
        )
        print(colored("M", "red") if issue["oid"] in modified_issues else " ", end="  ")
        print(format_labels(sorted(issue["labels"]), label_info))


def format_labels(labels, label_info):
    out = []
    for l in labels:
        if l not in label_info:
            out.append((l, None, None))
        elif not all(i in label_info[l] for i in ("bgcolor", "fgcolor")):
            out.append((l, None, None))
        else:
            out.append((l, label_info[l]["fgcolor"], label_info[l]["bgcolor"]))
    return " ".join(colored(*i, attrs=["reverse"]) for i in out)


def check_priority(ctx, param, value):
    try:
        return int(value)
    except:
        try:
            return float(value)
        except:
            raise click.BadParameter("priority must be an integer or a decimal number")


@click.command(name="new")
@click.option(
    "-t",
    "--title",
    prompt="Title",
    help="the title of this issue (if none is provided, you will be prompted to enter one)",
)
@click.option(
    "-p",
    "--priority",
    callback=check_priority,
    default=0,
    help="this issue's priority, as an integer or decimal number (default: 0)",
)
@click.option(
    "-a",
    "--assignee",
    multiple=True,
    help="a person assigned to this issue (can be given multiple times)",
)
@click.option(
    "-l",
    "--label",
    multiple=True,
    help="a label associated with this issue (can be given multiple times)",
)
@click.option(
    "-r", "--target", type=str, default=None, help="this issue's target (default: None)"
)
@click.option(
    "-e",
    "--empty",
    is_flag=True,
    default=False,
    help="create an issue with an empty body",
)
@click.option(
    "-s",
    "--stdin",
    is_flag=True,
    default=False,
    help="read body from stdin rather than opening an editor",
)
def new_issue(title, priority, assignee, label, target, empty, stdin):
    """
    Create a new issue
    """
    title = title.strip()
    if not title:
        click.echo(colored("ERROR: no title supplied.", "red"), err=True)
        sys.exit(1)

    repo_info = find_repo_helper(error_on_no_identity=True)

    params = {
        "priority": priority,
        "assignees": set(assignee),
        "labels": set(label),
        "target": target,
    }

    body = "" if empty else body_from_stdin_or_editor(stdin)

    try:
        issue_id, action_id = commands.new_issue(
            repo_info["root"], repo_info["name"], title, body, params
        )
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)
    click.echo(colored("Created issue %s" % issue_id, "green"))


@click.command()
@click.argument("issue")
@click.argument("label", nargs=-1)
@click.option(
    "-d", "--delete", is_flag=True, help="Remove labels instead of adding them"
)
def label(issue, label, delete):
    """
    Add or remove labels from an issue
    """

    if not label:
        click.echo(colored("No labels provided.  Exiting"))
        sys.exit(0)

    repo_info = find_repo_helper(error_on_no_identity=True)

    try:
        issue = data.get_issue_state(repo_info["root"], issue)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    label = set(label)
    valid_labels = set()
    for l in label:
        try:
            data.valid_label_name(l)
            valid_labels.add(l)
        except data.HiveDataException as e:
            click.echo(
                colored("Invalid label name %r, not adding." % l, "magenta"), err=True
            )

    if valid_labels:
        func = commands.remove_labels if delete else commands.add_labels
        try:
            new_id = func(
                repo_info["root"], repo_info["name"], issue["id"], valid_labels
            )
        except data.HiveDataException as e:
            click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
            sys.exit(1)

        if delete:
            click.echo(
                colored(
                    "Removed the following labels from issue %s:" % (issue["id"],),
                    "green",
                )
            )
        else:
            click.echo(
                colored(
                    "Added the following labels to issue %s:" % (issue["id"],), "green"
                )
            )
        click.echo(
            format_labels(valid_labels, data.label_information(repo_info["root"]))
        )


@click.command()
@click.argument("issue")
@click.argument("assignee", nargs=-1)
@click.option(
    "-d", "--delete", is_flag=True, help="Remove assignees instead of adding them"
)
@click.option(
    "-m",
    "--me",
    is_flag=True,
    help="Add/remove yourself to/from the issue, rather than providing names",
)
def assign(issue, assignee, delete, me):
    """
    Add or remove assignees from an issue
    """
    repo_info = find_repo_helper(error_on_no_identity=True)

    if me:
        assignee = [repo_info["name"]]
    if not assignee:
        click.echo(colored("No assignees provided.  Exiting"))
        sys.exit(0)

    try:
        issue = data.get_issue_state(repo_info["root"], issue)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    func = commands.remove_assignees if delete else commands.add_assignees
    try:
        new_id = func(repo_info["root"], repo_info["name"], issue["id"], set(assignee))
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    if delete:
        click.echo(colored("Unassigned from issue %s:" % (issue["id"],), "green"))
    else:
        click.echo(colored("Assigned to issue %s:" % (issue["id"],), "green"))
    for a in assignee:
        click.echo(a)


@click.command()
@click.argument("issue")
@click.option(
    "-s",
    "--stdin",
    is_flag=True,
    default=False,
    help="read body from stdin rather than opening an editor",
)
@click.option(
    "-r",
    "--reply-to",
    type=str,
    default=None,
    help="the ID of a comment to respond to (if not specified, make a new top-level comment)",
)
@click.option(
    "-e",
    "--edit",
    type=str,
    default=None,
    help="the ID of a comment to edit (instead of making a new comment)",
)
def comment(issue, stdin, reply_to, edit):
    """
    Create or edit comments on the given issue
    """
    repo_info = find_repo_helper(error_on_no_identity=True)

    try:
        issue = data.get_issue_state(repo_info["root"], issue)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    if edit is None:
        initial_md = ""
        allow_empty = False
    else:
        try:
            edit = data.real_comment_id(repo_info["root"], issue["id"], edit)
            initial_md = issue["comments_by_id"][edit]["body"]
            allow_empty = True
        except data.HiveDataException as e:
            click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
            sys.exit(1)

    if reply_to is not None:
        try:
            reply_to = data.real_comment_id(repo_info["root"], issue["id"], reply_to)
        except data.HiveDataException as e:
            click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
            sys.exit(1)

    body = body_from_stdin_or_editor(
        stdin, initial_md=initial_md, allow_empty=allow_empty
    )

    if edit is None:
        try:
            new_id = commands.add_comment(
                repo_info["root"], repo_info["name"], issue["id"], body, parent=reply_to
            )
        except data.HiveDataException as e:
            click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
            sys.exit(1)

        click.echo(
            colored("Created comment %s on issue %s" % (new_id, issue["id"]), "green")
        )
    else:
        try:
            new_id = commands.edit_comment(
                repo_info["root"], repo_info["name"], issue["id"], edit, body
            )
        except data.HiveDataException as e:
            click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
            sys.exit(1)

        click.echo(
            colored("Edited comment %s on issue %s" % (edit, issue["id"]), "green")
        )


def command_helper(issue, func, success_msg, *args, **kwargs):
    repo_info = find_repo_helper(error_on_no_identity=True)

    try:
        issue = data.get_issue_state(repo_info["root"], issue)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    try:
        func(repo_info["root"], repo_info["name"], issue["id"], *args, **kwargs)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)
    click.echo(colored(success_msg(issue), "green"))


@click.command()
@click.argument("issue")
@click.argument("priority", callback=check_priority)
def priority(issue, priority):
    """
    Set an issue's priority
    """
    command_helper(
        issue,
        commands.set_priority,
        lambda i: "Set issue %s priority to %s" % (i["id"], priority),
        priority,
    )


@click.command()
@click.argument("issue")
@click.option(
    "-c",
    "--comment",
    type=str,
    default=None,
    help="A comment to make before closing the issue",
)
def close(issue, comment):
    """
    Close a given issue
    """
    repo_info = find_repo_helper(error_on_no_identity=True)

    try:
        issue = data.get_issue_state(repo_info["root"], issue)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    if comment is not None:
        try:
            new_id = commands.add_comment(
                repo_info["root"], repo_info["name"], issue["id"], comment
            )
        except data.HiveDataException as e:
            click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
            sys.exit(1)

        click.echo(
            colored("Created comment %s on issue %s" % (new_id, issue["id"]), "green")
        )

    try:
        commands.close_issue(repo_info["root"], repo_info["name"], issue["id"])
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)
    click.echo(colored("Closed issue %s" % issue["id"], "green"))


@click.command(name="open")
@click.argument("issue")
def open_(issue):
    """
    Open/reopen a given issue
    """
    command_helper(issue, commands.open_issue, lambda i: "Opened issue %s" % (i["id"],))


@click.command()
@click.argument("issue")
@click.argument("target")
def target(issue, target):
    """
    Set an issue's target
    """
    command_helper(
        issue,
        commands.set_target,
        lambda i: "Set issue target for issue %s to %s" % (i["id"], target),
        target,
    )


@click.command()
@click.option(
    "-b",
    "--browser",
    is_flag=True,
    help="Launch a browser after starting the application",
)
@click.option(
    "--read-only",
    help="Launch the web interface in read-only mode (cannot modify issues)",
)
@click.option("-u", "--url-root", help="Root URL to prepend to links", default="")
def web(browser, read_only, url_root):
    """
    Start the web interface
    """
    repo_info = vcs.get_repo_info()
    app.config["repo_info"] = repo_info
    app.config["read_only"] = read_only
    app.config["url_root"] = url_root
    if browser:
        webbrowser.open_new("http://127.0.0.1:5000")
    app.run(debug=True)


def valid_color(ctx, param, value):
    hexchars = set("0123456789abcdef")
    value = value.strip().lower().lstrip("#")
    if value and (len(value) != 6 or any(i not in hexchars for i in value)):
        raise click.BadParameter(
            "color must be specified as 6 hex characters, e.g. ffffff"
        )
    return value


@click.command(name="edit-label")
@click.argument("label")
@click.option(
    "-d", "--description", help="description", prompt="Description", default=""
)
@click.option(
    "-b",
    "--bgcolor",
    help="background color (hex)",
    prompt="Background Color (hex, leave empty to use default)",
    callback=valid_color,
    default="",
)
@click.option(
    "-f",
    "--fgcolor",
    help="foreground color (hex)",
    prompt="Foreground (text) Color (hex, leave empty to use default)",
    callback=valid_color,
    default="",
)
def edit_label(label, description, bgcolor, fgcolor):
    """
    Edit the given label
    """
    repo_info = find_repo_helper(error_on_no_identity=True)
    vals = {"description": description, "bgcolor": bgcolor, "fgcolor": fgcolor}
    try:
        commands.edit_label(
            repo_info["root"], label, {k: v for k, v in vals.items() if v}
        )
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)
    click.echo(colored("Updated label %s" % label, "green"))


def valid_date(ctx, param, value):
    if value and not (re.match(r"\d{4}-\d{2}-\d{2}", value)):
        raise click.BadParameter("date must be specified as YYYY-MM-DD")
    return value


@click.command(name="edit-target")
@click.argument("target")
@click.option(
    "-d", "--description", help="description", prompt="Description", default=""
)
@click.option(
    "-u",
    "--due-date",
    help="due date (YYYY-MM-DD)",
    prompt="Due date (YYYY-MM-DD)",
    callback=valid_date,
    default="",
)
@click.option("--active/--inactive", "-a/-i", default=True)
def edit_target(label, description, due_date, active):
    """
    Edit the given target
    """
    repo_info = find_repo_helper(error_on_no_identity=True)
    vals = {"description": description, "due_date": due_date, "active": active}
    try:
        commands.edit_target(
            repo_info["root"], label, {k: v for k, v in vals.items() if v != ""}
        )
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)
    click.echo(colored("Updated target %s" % target, "green"))


@click.command()
def version():
    """
    Print version number and exit
    """
    print("hive version", __version__)


@click.command()
@click.option(
    "-m", "--message", help="The commit message to use", type=str, default=None
)
@click.option(
    "-a", "--add-only", help="Don't actually commit; just add files", is_flag=True
)
@click.option(
    "--pack/--no-pack",
    help="Flag to decide whether to pack untracked files or not (default behavior is to pack them together before committing)",
    default=True,
)
@click.option(
    "--pack-all",
    help="Pack all actions together (including those already tracked by the VCS) instead of just packing untracked files.  May lead to merge conflicts!!!",
    is_flag=True,
)
def commit(message, add_only, pack, pack_all):
    """
    Add all Hive-related files to the repository and commit.
    """
    repo_info = find_repo_helper(error_on_no_identity=True)

    if pack:
        vcs.pack(repo_info, untracked_only=(not pack_all))

    vcs.add(repo_info)
    if not add_only:
        vcs.commit(repo_info, message)


@click.command(name="build-cache")
def build_cache():
    """
    Cache the state of issues in the tracker
    """
    repo_info = find_repo_helper(error_on_no_identity=False)
    data.cached_all_issues(repo_info["root"], override_cache=True, progress=True)


@click.command()
@click.argument("issue")
@click.argument("fname", nargs=-1)
def pack(issue, fname):
    """
    Combine actions
    """
    repo_info = find_repo_helper(error_on_no_identity=True)

    issues = [issue] if issue != "all" else data.list_issues(repo_info["root"])

    for issue in issues:
        try:
            issue = data.get_issue_state(repo_info["root"], issue)
        except data.HiveDataException as e:
            click.echo(colored(e.args[0], "red"), err=True)
            continue

        try:
            new_id, num_actions = data.pack(
                repo_info["root"], issue["id"], "all" if not fname else fname
            )
        except data.HiveDataException as e:
            click.echo(colored(e.args[0], "red"), err=True)
            continue

        click.echo(
            colored(
                "Packed %d actions into %s in issue %s"
                % (num_actions, new_id, issue["id"]),
                "green",
            )
        )


@click.command()
@click.argument("issue")
@click.argument("fname")
def unpack(issue, fname):
    """
    Combine actions
    """
    repo_info = find_repo_helper(error_on_no_identity=True)

    try:
        issue = data.get_issue_state(repo_info["root"], issue)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    try:
        new_ids, num_actions = data.unpack(repo_info["root"], issue["id"], fname)
    except data.HiveDataException as e:
        click.echo(colored("ERROR: %s" % e.args[0], "red"), err=True)
        sys.exit(1)

    click.echo(
        colored("Unpacked %s into the following action files:" % num_actions, "green")
    )
    for n in new_ids:
        click.echo(colored(i, "green"))


main.add_command(init)
main.add_command(new_issue)
main.add_command(show)
main.add_command(list_)
main.add_command(comment)
main.add_command(label)
main.add_command(close)
main.add_command(open_)
main.add_command(priority)
main.add_command(target)
main.add_command(assign)
main.add_command(web)
main.add_command(edit_label)
main.add_command(edit_target)
main.add_command(version)
main.add_command(commit)
main.add_command(build_cache)
main.add_command(pack)
main.add_command(unpack)
