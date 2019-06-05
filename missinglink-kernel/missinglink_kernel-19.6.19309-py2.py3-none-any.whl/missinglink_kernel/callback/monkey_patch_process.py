# -*- coding: utf-8 -*-
import sys


class MonkeyPatchProcess(object):
    process_methods = [
        'execl', 'execle', 'execlp', 'execlpe', 'execv', 'execve', 'execvp', 'execvpe',
        'spawnl', 'spawnle', 'spawnlp', 'spawnlpe', 'spawnv', 'spawnve', 'spawnvp', 'spawnvpe']

    ml_monkey_prefix = 'ml_original_'
    pydev_monkey_prefix = 'original_'

    @classmethod
    def create_warn_multiproc(cls, func):
        def new_warn_multiproc(*args):
            return func(*args)

        return new_warn_multiproc

    @classmethod
    def unmonkey_process_functions(cls, disable_process_monkey_patch):
        import os

        if disable_process_monkey_patch:
            return

        def unmonkey_patch(mod, func_name):
            original_name = cls.pydev_monkey_prefix + func_name
            if not hasattr(mod, original_name):
                return

            ml_original_name = cls.ml_monkey_prefix + func_name

            if hasattr(mod, ml_original_name):
                return

            setattr(mod, ml_original_name, getattr(mod, func_name))
            setattr(mod, func_name, cls.create_warn_multiproc(getattr(mod, original_name)))

        for method in cls.process_methods:
            unmonkey_patch(os, method)

        if sys.platform != 'win32':
            unmonkey_patch(os, 'fork')
            try:
                # noinspection PyUnresolvedReferences
                import _posixsubprocess
                unmonkey_patch(_posixsubprocess, 'fork_exec')
            except ImportError:
                pass
        else:
            # Windows
            try:
                import _subprocess
            except ImportError:
                # noinspection PyUnresolvedReferences
                import _winapi as _subprocess

            unmonkey_patch(_subprocess, 'CreateProcess')

    @classmethod
    def restore_monkey_process_functions(cls, disable_process_monkey_patch):
        import os

        if disable_process_monkey_patch:
            return

        def restore_monkey_patch(mod, func_name):
            original_name = cls.pydev_monkey_prefix + func_name
            if not hasattr(mod, original_name):
                return

            ml_original_name = cls.ml_monkey_prefix + func_name

            if not hasattr(mod, ml_original_name):
                return

            setattr(mod, original_name, getattr(mod, func_name))
            setattr(mod, func_name, getattr(mod, ml_original_name))
            delattr(mod, ml_original_name)

        for method in cls.process_methods:
            restore_monkey_patch(os, method)

        if sys.platform != 'win32':
            restore_monkey_patch(os, 'fork')
            try:
                # noinspection PyUnresolvedReferences
                import _posixsubprocess
                restore_monkey_patch(_posixsubprocess, 'fork_exec')
            except ImportError:
                pass
        else:
            # Windows
            try:
                import _subprocess
            except ImportError:
                # noinspection PyUnresolvedReferences
                import _winapi as _subprocess

            restore_monkey_patch(_subprocess, 'CreateProcess')
