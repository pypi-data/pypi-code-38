#!/usr/bin/env python3

"""
@author: xi
@since: 2018-12-23
"""

import code
import collections
import os
import pickle
import sys
import threading

import numpy as np
import prettytable
import tensorflow as tf

from . import common


def shell(fn):
    fn.__name__ = f'{fn.__name__}<shell>'
    return fn


def _is_shell_fn(fn):
    return hasattr(fn, '__name__') and fn.__name__.find('<shell>') != -1


class Application(object):
    """Base class of an photinia application.
    The main use of this class is for "hot-tuning".

    Any code that need "hot-tuning" should be defined in the "_main(args)" method of the subclass of Application.
    Then you need to define checkpoints in that method.
    Here is an simple example:

    class Main(ph.Application):

        def _main(self, args):
            x = ph.variable('x', [[1, 2], [3, 4]])
            step = ph.Step(
                outputs=tf.reduce_sum(x),
                updates=tf.assign_add(x, np.ones((2, 2)))
            )
            ph.initialize_global_variables()

            for i in range(1000000000):
                print(step())
                time.sleep(0.5)
                self.checkpoint()

    """

    _has_instance_lock = threading.Semaphore(1)
    _has_instance = False

    def __init__(self):
        with self._has_instance_lock:
            if self._has_instance:
                raise RuntimeError('Only one Application instance is allowed.')
            self._has_instance = True

        self._args = None
        self._app_thread = None
        self._ret_code = -1

        self._local_dict = {}
        self._interrupt_lock = threading.Semaphore(1)
        self._interrupt = False

        self._main_dir = os.getcwd()
        self._shell_dir = os.getcwd()

        self._var_list = []
        self._var_dict = {}
        self._widget_list = []

    def __main(self, args):
        self._ret_code = self._main(args)

    def _main(self, args):
        raise NotImplementedError()

    def checkpoint(self):
        with self._interrupt_lock:
            if not self._interrupt:
                return

        local_dict = self._local_dict = collections.OrderedDict((
            (name, fn)
            for name, fn in ((name, getattr(self, name)) for name in dir(self))
            if _is_shell_fn(fn)
        ))
        local_dict['np'] = np
        local_dict['tf'] = tf
        self._main_dir = os.getcwd()
        os.chdir(self._shell_dir)
        code.interact(
            banner='\n',
            local=local_dict,
            exitmsg='\n'
        )
        self._shell_dir = os.getcwd()
        os.chdir(self._main_dir)

        with self._interrupt_lock:
            self._interrupt = False

    def run(self, args):
        self._args = args
        self._app_thread = threading.Thread(target=self.__main, args=(args,))
        self._app_thread.setDaemon(True)
        self._app_thread.start()
        while True:
            try:
                self._app_thread.join()
                break
            except KeyboardInterrupt:
                with self._interrupt_lock:
                    if self._interrupt:
                        continue
                    self._interrupt = True
                    print('Waiting for the checkpoint...')
        return self._ret_code

    @shell
    def vars(self, prefix=''):
        """List variables."""
        var_dict = self._var_dict = {
            var_.name: var_
            for var_ in tf.global_variables()
        }
        vars_list = self._var_list = [
            var_
            for name, var_ in var_dict.items()
            if name.startswith(prefix)
        ]
        table = prettytable.PrettyTable([
            '#',
            'Name',
            'Shape',
            'dtype',
            'Trainable'
        ])
        for i, var_ in enumerate(vars_list, 1):
            table.add_row((
                i,
                var_.name,
                var_.shape,
                var_.dtype.name,
                var_.trainable
            ))
        print(table)
        print()

    @shell
    def tvars(self, prefix=''):
        """List trainable variables."""
        self._var_dict = {
            var_.name: var_
            for var_ in tf.global_variables()
        }
        vars_list = self._var_list = [
            var_
            for var_ in tf.trainable_variables()
            if var_.name.startswith(prefix)
        ]
        table = prettytable.PrettyTable([
            '#',
            'Name',
            'Shape',
            'dtype'
        ])
        for i, var_ in enumerate(vars_list, 1):
            table.add_row((
                i,
                var_.name,
                var_.shape,
                var_.dtype.name
            ))
        print(table)
        print()

    @shell
    def value(self, var_id, value=None):
        """Get/Set the value of the specific variable."""
        var_ = self._get_variable(var_id)
        if value is None:
            return common.get_session().run(var_)
        else:
            dest_shape = var_.shape
            if isinstance(value, (int, float)):
                value = np.full(dest_shape, value)
            if not isinstance(value, np.ndarray):
                value = np.array(value)
            if value.shape != dest_shape:
                print(f'Incompatible shape: {dest_shape} and {value.shape}.', file=sys.stderr)
                return
            var_.load(value, common.get_session())

    @shell
    def echo(self, var_id):
        """Show value of the specific variable."""
        var_ = self._get_variable(var_id)
        value = common.get_session().run(var_)
        shape = value.shape
        if len(shape) == 0:
            print(f'{var_.name} = {value}')
        elif len(shape) == 2 and shape[0] <= 50 and shape[1] <= 50:
            table = prettytable.PrettyTable(
                header=False,
                hrules=prettytable.ALL,
                vrules=prettytable.ALL
            )
            for row in value:
                table.add_row(
                    tuple(f'{cell:.04f}' for cell in row)
                )
            print(f'{var_.name} =')
            print(table)
        else:
            value = np.mean(np.abs(value))
            print(f'|{var_.name}| = {value}')
        print()

    def _get_variable(self, var_id):
        if isinstance(var_id, int):
            try:
                return self._var_list[var_id - 1]
            except IndexError:
                print('No such variable.', file=sys.stderr)
                return
        elif isinstance(var_id, str):
            try:
                return self._var_dict[var_id]
            except KeyError:
                print('No such variable.', file=sys.stderr)
                return
        else:
            print(f'Invalid var_id={var_id}', file=sys.stderr)
            return

    @shell
    def widgets(self, prefix=''):
        """List widgets."""
        with common.Trainable.instance_lock:
            widget_list = self._widget_list = [
                (name, widget)
                for name, widget in common.Trainable.instance_dict.items()
                if name.startswith(prefix)
            ]
        # widget_list.sort(key=lambda a: a[0])
        table = prettytable.PrettyTable(['#', 'Name', 'Type'])
        for i, (name, widget) in enumerate(widget_list, 1):
            table.add_row([i, name, widget.__class__.__name__])
        print(table)
        print()

    @shell
    def widget(self, widget_id):
        """Get a specific widget."""
        if isinstance(widget_id, int):
            try:
                return self._widget_list[widget_id - 1][1]
            except IndexError:
                print('No such widget.', file=sys.stderr)
                return
        elif isinstance(widget_id, str):
            try:
                with common.Trainable.instance_lock:
                    return common.Trainable.instance_dict[widget_id]
            except KeyError:
                print('No such widget.', file=sys.stderr)
                return
        else:
            print(f'Invalid widget_id={widget_id}', file=sys.stderr)
            return

    @shell
    def model_show(self, model_file):
        """Show structure of a specific model file."""
        with open(model_file, 'rb') as f:
            param_dict = pickle.load(f)
        param_list = [(k, v) for k, v in param_dict.items()]
        param_list.sort(key=lambda a: a[0])
        table = prettytable.PrettyTable(['Name', 'Shape'])
        for name, value in param_list:
            table.add_row((name, str(value.shape)))
        print(table)
        print()

    @shell
    def model_dump(self, model, model_file):
        """Dump the model."""
        model.dump(model_file)

    @shell
    def pwd(self):
        """Show the path of the current directory."""
        print(os.getcwd())
        print()

    @shell
    def ls(self, dir_='.'):
        """List files of the current directory."""
        for filename in os.listdir(dir_):
            file_ = os.path.join(dir_, filename)
            if os.path.isdir(file_):
                print(filename + '/')
            else:
                print(filename)
        print()

    @shell
    def cd(self, dir_=None):
        """Change current directory."""
        if dir_ is None:
            os.chdir(self._main_dir)
        else:
            os.chdir(dir_)

    @shell
    def help(self):
        """Show this help."""
        print('When caught in a desperation, the only person who can save you is yourself.')
        table = prettytable.PrettyTable(['Method', 'Description'])
        table.align['Description'] = 'l'
        for name, obj in self._local_dict.items():
            if name.startswith('_'):
                continue
            doc = obj.__doc__
            if doc is None or len(doc) > 100:
                #
                # prevent empty doc or too long string
                continue
            table.add_row((name, doc))
        print(table)
        print()
