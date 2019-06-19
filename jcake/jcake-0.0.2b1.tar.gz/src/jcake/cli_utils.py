#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import crayons


def format_help(help):
    """Formats the help string."""
    help = help.replace("Options:", str(crayons.white("Options:", bold=True)))
    help = help.replace(
        "Usage: jcake",
        str("Usage: {0}".format(crayons.white("jcake", bold=True)))
    )
    help = help.replace(
        "  create",
        str(crayons.green("  create", bold=True))
    )
    additional_help = """
Usage Examples:
   Create new Java project for developing Module
   $ {0}

   Create new Java project for developing MicroService
   $ {1}

Commands:""".format(
        crayons.red("jcake create"),
        crayons.red("jcake create --ms")
    )
    help = help.replace("Commands:", additional_help)
    return help
