#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''
Summary
-------
Clean up and format C/C++ source code using GNU indent.

Usage
-----
Source code from C/C++ tasks can cleaned and formatted according to the
specified rules (default is *GNU* style) using the following command::

        $ waf indent --targets=<task>

When cleaning only those task specified using the '--targets=' option
will be cleaned. The default is to clean all task within the entire build 
environment. Specific C/C++ task can be permanently excluded from cleaning
using the 'indent_skipme' as attribute for those tasks.

formatting rules can be specified the using a 'indent.pro' file using the
options as described for GNU indent. These global rules can used by this
module when using the '--indent-pro=<path-to-indent-pro' option at 
configuration time.

''' 


import os
from waflib import Scripting, Logs, Utils
from waflib.Build import BuildContext


def indent_cleanup(self):
    if self.options.indent_cleanup:
        return True
    return self.env.INDENT_CLEANUP[0]


def options(opt):
    opt.add_option('--indent-pro', dest='indent_pro',
        default=None, action='store', help='path to .indent.pro file')
    opt.add_option('--indent-cleanup', dest='indent_cleanup',
        default=False, action='store_true', help='cleanup GNU indent backup files')


def configure(conf):
    ret = conf.find_program('indent', var='INDENT', mandatory=False)
    if ret:
        profile=conf.options.indent_pro
        if profile:
            if not os.path.exists(profile):
                conf.fatal('file not found: --indent-pro=%s' % profile)
        else:
            profile = conf.find_file('.indent.pro', path_list=['.', dict(os.environ)['HOME'] ], mandatory=False)
            if not profile:
                profile = conf.find_file('indent.pro', path_list=['.', dict(os.environ)['HOME'] ], mandatory=False)
        if profile:
            profile = os.path.abspath(profile)
            conf.env.INDENT_PROFILE = profile
        
        conf.env.INDENT_CLEANUP = [conf.options.indent_cleanup]


class GnuIndentContext(BuildContext):
    '''format C/C++ source code using GNU indent.'''
    cmd = 'indent'
    fun = Scripting.default_cmd

    def execute(self):
        '''Entry point when executing the command (self.cmd).
        
        Format C/C++ source code and headers using GNU indent.
        '''
        self.restore()
        if not self.all_envs:
            self.load_envs()
        self.recurse([self.run_dir])

        if not self.env.INDENT:
            self.fatal('GNU indent not found; please install it and reconfigure')
            return

        targets = self.targets.split(',') if self.targets!='' else None

        for group in self.groups:
            for tgen in group:
                if targets and tgen.name not in targets:
                    continue
                if getattr(tgen, 'indent_skipme', False):
                    continue
                if not set(('c', 'cxx')) & set(getattr(tgen, 'features', [])):
                    continue
                (sources, headers) = self.get_files(tgen)
                self.exec_indent(tgen, sources, headers)

    def get_files(self, tgen):
        '''returns a tuple containing a list of source and header filenames
        defined for the given task generator.

        :param tgen: Task for which the input file names should be returned.
        :type tgen: waflib.Task.TaskGenerator
        
        :returns: tuple containing source and header files of given task.
        :rtype: tuple(str, str, ..)
        '''
        sources = tgen.to_list(getattr(tgen, 'source', []))
        sources = [tgen.path.find_node(s) if isinstance(s, str) else s for s in sources]
        sources = [s.abspath() for s in sources]

        headers = []
        for include in tgen.to_list(getattr(tgen, 'includes', [])):
            node = tgen.path.find_node(include)
            if not node:
                Logs.warn("WARNING task(%s): include directory '%s' does not exist" % (tgen.name, include))
            else:
                for header in node.ant_glob('*.h'):
                    headers.append(header.abspath())
        return (list(set(sources)), list(set(headers)))

    def indent(self, tgen, files, env, cleanup=False):
        '''execute GNU indent source code formater on given files names.

        :param tgen: Task of which input files should be formatted
        :type tgen: waflib.Task.TaskGenerator
        
        :param files: list of paths to source and header files
        :type files: list(str, str, ..)
        :param env: OS environment to be used when invoking indent
        :type env: dict
        :param cleanup: remove backup files (*~) when true
        :type cleanup: bool
        '''
        command = '%s' % Utils.to_list(self.env.INDENT)[0]
        for f in files:
            cmd = '%s %s' % (command, os.path.basename(f))
            cwd = os.path.dirname(f)
            Logs.info("--> indent(%s)" % (f))
            err = self.exec_command(cmd, cwd=cwd, env=env)
            if err:
                self.fatal("indent(%s): failure on '%r', err=%s" % (tgen.name, f, err))
            if cleanup:
                if hasattr(f, 'abspath'): os.remove('%s~' % f.abspath())
                else: os.remove('%s~' % f)


    def exec_indent(self, tgen, sources, headers):
        '''execute GNU indent on the source and include files of task generator

        :param tgen:        task of which the source code should be beautified
        :type tgen:         waflib.Task.TaskGenerator
        :param sources:     list of source file names
        :type sources:      list(str, str, ..)
        :param headers:     list of include file names
        :type headers:      list(str, str, ..)
        '''
        env = dict(os.environ)
        if self.env.INDENT_PROFILE:
            env['INDENT_PROFILE'] = self.env.INDENT_PROFILE
        cleanup = indent_cleanup(self)

        Logs.info("indent(%s): formatting code" % tgen.name)
        Logs.info("$INDENT_PROFILE = %s" % env['INDENT_PROFILE'] if 'INDENT_PROFILE' in env else '')
        self.indent(tgen, sources, env, cleanup)
        self.indent(tgen, headers, env, cleanup)
        Logs.info("indent(%s): finished" % tgen.name)

