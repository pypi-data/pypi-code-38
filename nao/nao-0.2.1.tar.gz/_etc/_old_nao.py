# -*- coding: utf-8 -*-
"""
this should be a basic package that
reads everything from a directory
structure (data lazy) and provide
a flexible object model to access
all the resources


- data files (rst, yaml, csv, xlsx, etc)
    rst needs support for :ref: inside nao datastructure
    add rst parsing to yaml files, also support cross yaml referencing with rst style tags
- database connections (sqlite, special yaml files using, sqlalchemy models?)
- automatically serve those files as a webserver
- python files for code support (no relative import only through nao.self?)
    - decorators to provide functionality outside (e.g. auth, etc)
- template files made available automatically (in nao.current.template)

later multilayer support should be added
the main resaon for that is supporting
multilingualism (also production, testing separation)

multilingualism is supported by babel negotiatble tags(e.g. en_US)

mode separation is set up based on _identifier style tags

"""
from __future__ import unicode_literals # no need in python3 stack

# basic logging
import os
import sys
import logging
import time
import functools
import codecs
import re
import collections

# from future.utils import python_2_unicode_compatible

from .utils import obj2xml, recursive_update, padded
from .types import odict, naodict, nao

from ._yaml import load as load, dump as dump

# get rid of __pycache__ for all
sys.dont_write_bytecode = True

op = os.path

import pathlib


def _load(source=None):
    """
    main entry point, loads everything from a given point
    of the file system (usually __file__)

    builds a tree based on file names and parse
    files based on extension and alphabetical
    order

    .yaml
        regular python data
        with some type of nao reference type available
        maybe all text fields interpreted as rst is a good idea
        add protocol handling as well (file://, ext://, oracle://, ...)
        see `logging.config.dictConfig` for reference

    .rst
        parsed as in sphinx docs into raw html
        :nao:`something` should be available

    .csv, .sql, .xls, .xlsx
        deferred datatable
        sql should run on the default db connection
        defined by nao-tree (with special .nao files)
        if nothing defined .nao-s own default sqlite
        db should be used (cashing, etc also in that)
    
    .nao
        special resource described in YAML
        e.g. database connaction, RPC service, aPI calls, etc.
        return a Python object???
        similar .rst's and .yaml's ext directive

    .html, .jinja
        parsed as jinja templates by default
        the object returned in load is available by the
        name nao in tempate global (think it over more)

    .py
        parsed as python code and an object tree
        is build (I know this is going to be controversial...)

    .jpg, .png, .mp3, .wav, .avi, ...
        parsed as media resource (embed in template)


    read system information as well and do
    everything in a multilayer and cascading
    manner

    returns a root element
    """
    if source is None:
        # doubles the check for existence, but avoids strange errors
        if op.exists('nao'):
            source = 'nao'

        # TODO check for nao.yaml, nao/, config.yaml, config/
        # in some order defined as a cutomizable parameter

        # finally load current directory as a config directory


    if isinstance(source, pathlib.Path):

        with source.open() as f:

            return yaml_load(f)
            

    if op.exists(source):
        if op.isdir(source):
            # log.debug("Loading from directory recursively")
            pass
            # TODO implement recursive directory loading
            # see Naopath.filter
        else:
            # log.debug("Loading from single file")
            with codecs.open(source, encoding='utf8') as f:
                # TODO add content negotiation here
                return yaml_load(f)

    else:
        # log.debug("Loading from string")

        # TODO create yaml naodictloader

        return yaml_load(source)

    # if source == None, then try to load [cwd]/nao

    # get directory based on source

    # create root_node of current directory
    # walk recursively, skip everything that starts with _
    # create nao* object-tree

    # nao.path(data.config.general)
    # str(data.config) # returns a path if it is a file/directory
    # nao.url(naobject :)


