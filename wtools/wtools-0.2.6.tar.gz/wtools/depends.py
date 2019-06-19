#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''
Summary
-------
xxxx

TODO: NOT FINISHED YET, WORK IN PROGRESS

Description
-----------
xxxx

Usage
-----
xxxx

In order to use this waftool simply add it to the *options* and *configure*
functions of your top level **wscript** file as shown in the example below::

    import waftools

    def options(opt):
        opt.load('tree', tooldir=waftools.location)

    def configure(conf):
        conf.load('tree')

When configured as shown in the example above, the *tree* command can be issued 
on all targets, a single target or a range of targets::

    $ waf tree --targets=blib

'''

from waflib import Logs, Build, Scripting, Errors


def options(opt):
	opt.add_option('--depends-outdir', dest='depends_outdir', default=None, action='store', help='location to store depends report')

class DependsContext(Build.BuildContext):
    '''store (external) task dependencies to file'''
    cmd = 'depends'
    fun = Scripting.default_cmd

    def _get_task_generators(self):
        '''Returns a list of task generators for which the command should be executed
        '''
        taskgenerators = []
        if len(self.targets):
            for target in self.targets.split(','):
                taskgen = self.get_tgen_by_name(target)
                taskgenerators.append(taskgen)
        else:
            for group in self.groups:
                for taskgen in group:
                    taskgenerators.append(taskgen)
        return list(set(taskgenerators[:]))

    def execute(self):
        '''Entry point when executing the command (self.cmd).
        
        Displays a list of dependencies for each specified task
        '''
        self.restore()
        if not self.all_envs:
            self.load_envs()
        self.recurse([self.run_dir])

        for taskgen in self._get_task_generators():
            taskgen.post()
            Logs.info('')
            self.print_tree(taskgen, '    ')
        self.print_legend()

    def get_childs(self, parent):
        '''Returns a list of task generator used by the parent.
        
        :param parent: task generator for which the childs should be returned
        :type parent: waflib.TaskGen
        '''
        childs = []
        names = parent.to_list(getattr(parent, 'use', []))
        for name in names:
            try:
                child = self.get_tgen_by_name(name)
                childs.append(child)
            except Errors.WafError:
                Logs.error("skipping dependency '%s'; task does not exist" % name)
        return childs

    def print_tree(self, parent, padding):
        '''Display task dependencies in a tree like manner
        
        :param parent: task generator for which the dependencies should be listed
        :type parent: waflib.TaskGen
        :param padding: tree prefix (i.e. amount of preceeding whitespace spaces)
        :type padding: str
        '''
        Logs.warn('%s+-%s' % (padding[:-1], parent.name))
        padding = padding + ' '

        for task in parent.tasks:
            for node in task.dep_nodes:
                Logs.info('%s│' % (padding))
                if self.options.tree_loc:
                    Logs.info('%s│<-- %r' % (padding, node))
                else:
                    Logs.info('%s│<-- %s' % (padding, node))

            for output in task.outputs:
                Logs.info('%s│' % (padding))
                if self.options.tree_loc:
                    Logs.info('%s│--> %r' % (padding, output))
                else:
                    Logs.info('%s│--> %s' % (padding, output))

        for lib in parent.to_list(getattr(parent,'lib', [])):
            Logs.info('%s│' % (padding))
            Logs.info('%s│<-- %s (lib)' % (padding,lib))

        childs = self.get_childs(parent)
        count = 0
        for child in childs:
            count += 1
            Logs.info('%s│' % padding)
            if count == len(childs):
                self.print_tree(child, padding + ' ')
            else:
                self.print_tree(child, padding + '│')

    def print_legend(self):
        '''Displays description for the tree command.'''
        Logs.info("")
        Logs.info("")
        Logs.info("DESCRIPTION:")
        Logs.info("m (lib)   = uses system library 'm' (i.e. libm.so)")
        Logs.info("-->       = task output; i.e. produces")
        Logs.info("<--       = task input; i.e. consumes, requires and/or uses")
        Logs.info("")

