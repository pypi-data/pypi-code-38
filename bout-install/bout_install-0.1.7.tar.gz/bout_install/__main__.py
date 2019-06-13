#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bout_install.main import bout_install_command_line

# NOTE: No __name__ == '__main__' to avoid double import trap
# https://stackoverflow.com/questions/43393764/python-3-6-project-structure-leads-to-runtimewarning/45070583#45070583
bout_install_command_line()
