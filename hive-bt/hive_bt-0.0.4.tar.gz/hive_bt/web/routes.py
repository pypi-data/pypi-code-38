import re
import cgi
import shlex
import markdown

from datetime import datetime
from flask import render_template, request
from markdown.extensions import tables, fenced_code, sane_lists

from . import app
from .. import __version__ as version
from .. import data
from .. import commands
from .. import util


def do_markdown(x):
    start = markdown.markdown(
        x,
        extensions=[
            tables.TableExtension(),
            fenced_code.FencedCodeExtension(),
            sane_lists.SaneListExtension(),
        ],
    )
    return start.replace("<script", "&lt;script").replace("</script", "&lt;/script")


@app.route("/")
def list_issues():
    read_only = app.config.get("read_only", False)
    repo_info = app.config["repo_info"]
    all_labels = data.label_information(repo_info["root"])
    sorts = [i for i in request.args.get("sorts", "").split(",") if i]
    filters = shlex.split(request.args.get("filters", ""))
    new_filters = []
    for i in filters:
        i = i.lower()
        for filt in data.filter_funcs:
            if i.startswith("%s:" % filt):
                new_filters.append(tuple(i.split(":", 1)))
                break
        else:
            new_filters.append(("any", i))
    all_issues = data.all_issues_state(
        repo_info["root"], sorts=sorts, filters=new_filters
    )
    prefixes = util.unique_prefixes(data.list_issues(repo_info["root"]))
    for i in all_issues:
        i["shortid"] = prefixes[i["id"]]

        i["time"] = util.format_time(i["updated_times"][0][1])
    return render_template(
        "main.html",
        repo_info=repo_info,
        version=version,
        issues=all_issues,
        filters=request.args.get("filters", ""),
        markdown=do_markdown,
        len=len,
        sorted=sorted,
        read_only=read_only,
        all_labels=all_labels,
        url_root=app.config.get("url_root", ""),
    )


def render_comment(config, issue_id, c, readonly):
    return """<div class="comment" id="comment-%s"><p><small>%s commented at %s:</small></p>
    %s
    %s
    <p><small><a href="%s/issue/%s#comment-%s">Permalink</a></small></p>
    </div>""" % (
        c["id"],
        cgi.escape(c["authors"][0]),
        util.format_time(c["display_time"]),
        do_markdown(c["body"]),
        "\n".join(
            render_comment(config, issue_id, child, readonly)
            for child in c.get("children", [])
        ),
        config.get("url_root", ""),
        issue_id,
        c["id"],
    )


@app.route("/issue/<issue_id>")
def show_issue(issue_id):
    read_only = app.config.get("read_only", False)
    repo_info = app.config["repo_info"]
    all_labels = data.label_information(repo_info["root"])
    issue = data.get_issue_state(repo_info["root"], issue_id)
    issue["time"] = util.format_time(issue["updated_times"][0][1])
    issue["utime"] = util.format_time(issue["updated_times"][-1][1])
    issue["rendered_comments"] = "\n\n".join(
        render_comment(app.config, issue["id"], i, read_only) for i in issue["comments"]
    )
    return render_template(
        "issue.html",
        repo_info=repo_info,
        version=version,
        issue=issue,
        markdown=do_markdown,
        len=len,
        read_only=read_only,
        sorted=sorted,
        all_labels=all_labels,
        url_root=app.config.get("url_root", ""),
    )
