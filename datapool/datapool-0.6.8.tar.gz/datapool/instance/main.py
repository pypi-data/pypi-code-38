#! /usr/bin/env python
# encoding: utf-8
from __future__ import print_function, division, absolute_import

# Copyright © 2018 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import click


def print_banner(function):
    import pkg_resources as p

    version = p.require("datapool")[0].version

    def inner(*a, **kw):
        import inspect

        command_name = inspect.stack()[2].frame.f_locals.get("self").name
        print()
        click.secho("> this is datapool version {}".format(version), fg="green")
        click.secho("> {}".format(command_name), fg="blue")
        return function(*a, **kw)

    # click needs this to generate help texts from doc strings:
    inner.__doc__ = function.__doc__
    return inner
