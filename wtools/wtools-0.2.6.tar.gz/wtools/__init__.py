#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os

version = "0.2.6"
location = os.path.abspath(os.path.dirname(__file__))


def install_dirs(bld, dirs, mode=0o755):
    '''Create all directories in the install prefix when needed
   
    :param bld: a *waf* build instance from the top level *wscript*
    :type bld: waflib.Build.BuildContext
    :param dirs: list of paths to create in the installation prefix
    :type dirs: list
    :param mode: access mode for the directories to be created
    :type mode: octal number
    '''
    if not bld.cmd.startswith('install'):
        return
    
    prefix = bld.env.PREFIX

    for d in dirs:
        path = os.path.join(prefix, d)
        if not os.path.exists(path):
            os.makedirs(path, mode=mode)


def get_rpath(bld, paths=['/lib', '/usr/lib', '/usr/local/lib'], relpaths=['lib', 'usr/lib'], always=False):
    '''Returns a list of paths to be included as search path for shared libraries

    Adds paths relative to the origin to the search path as well for host system and 
    current build is a debug build OR the always flag has been specified 
	
    :param bld: a *waf* build instance from the top level *wscript*
    :type bld: waflib.Build.BuildContext
    :param paths: list of (absolute) paths to use when searching for shared libraries 
    :type paths: list
    :param relpaths: list of (relative) paths to use when searching for shared libraries 
    :type relpaths: list
    :param relpaths: when true always add relative search paths 
    :type relpaths: bool
    :returns: list of directories to search for shared libraries
    '''
    if bld.env.DEST_OS == 'win32':
        return []

    if not always:
        if "NDEBUG" in bld.env.DEFINES:
            return paths

        if not bld.env.DEST_CPU in ['i386', 'i586', 'i686', 'x86_64']:
            return paths

    prefix = bld.env.PREFIX
    if not os.path.exists(prefix):
        os.makedirs(prefix)

    home = os.path.expanduser('~')
    rpaths = ['$ORIGIN/../%s' % p for p in relpaths]
    pnode = bld.root.find_dir(prefix)
    epath = os.path.realpath('%s/lib' % bld.env.EROOT)

    if os.path.exists(epath) and epath.startswith(home):
        epath = '$ORIGIN/%s' % bld.root.find_dir(epath).path_from(pnode)
        rpaths.append(epath)

    for lpath in bld.env.LIBPATH:
        if lpath.startswith(home):
            if not os.path.exists(lpath):
                continue
            lpath = '$ORIGIN/../%s' % bld.root.find_dir(lpath).path_from(pnode)
        rpaths.append(lpath)

    rpaths.extend(paths)
        
    if bld.env.LIBDIR.endswith('lib64'):
        rpaths = ["%s64" % p for p in rpaths]

    return rpaths

