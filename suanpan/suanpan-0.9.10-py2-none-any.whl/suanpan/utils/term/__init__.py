# coding=utf-8
from __future__ import absolute_import, print_function

from tabulate import tabulate

from suanpan.utils.term import graph


def chart(data, labels=None, colors=None, **kwargs):
    args = {
        "filename": "-",
        "title": None,
        "width": 50,
        "format": "{:<5.2f}",
        "suffix": "",
        "no_labels": not bool(labels),
        "color": None,
        "vertical": False,
        "stacked": False,
        "different_scale": False,
        "calendar": False,
        "start_dt": None,
        "custom_tick": "",
        "delim": "",
        "verbose": False,
        "version": False,
    }
    args.update(kwargs)
    colors = colors or []
    labels = labels or [None] * len(data)
    if args["calendar"]:
        graph.calendar_heatmap(data, labels, args)
    else:
        graph.chart(colors, data, args, labels)


def table(data, headers=(), theme="plain"):
    print(tabulate(data, headers=headers, tablefmt=theme))
