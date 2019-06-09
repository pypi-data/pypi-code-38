# -*- coding: utf-8 -*-

"""Top-level package for clasp."""

__author__ = """Stephen Wasilewski"""
__email__ = 'stephanwaz@gmail.com'
__version__ = '0.2.5'
__all__ = ['script_tools', 'click_ext', 'sphinx_click_ext']

import click
import clasp.click_ext

click = clasp.click_ext.click_ext(click)