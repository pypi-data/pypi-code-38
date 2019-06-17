import sys
import time
import threading
import types

import six
import os
import inspect
import site
import weakref
import imp

from collections import defaultdict

from rook.services.exts.cloud_debug_python.module_explorer import _GetLineNumbers
from six.moves import builtins

from rook.logger import logger

from rook.config import ImportServiceConfig

from rook.serverless import on_lambda

_SUPPORTED_PY_FORMATS = ['.py', '.pyc']

_BLACKLISTED_PATHS = []


class CountingImportLock(object):
    """
    When locked, only this thread can import (so all imports are guaranteed to have completed,
                                              and there are no partially initialized modules in sys.modules)
    """
    def __init__(self):
        self._count = 0

    def __enter__(self):
        imp.acquire_lock()
        self._count += 1

    def __exit__(self, *args, **kwargs):
        self._count -= 1
        imp.release_lock()

    def get_recursion_count(self):
        return self._count


class ImportService(object):

    NAME = "Import"

    class Notification(object):
        def __init__(self, module_name, module_filename, include_externals, lineno, callback, removed):
            self.module_name = module_name
            self.module_filename = module_filename
            self.callback = callback
            self.removed = removed
            self.include_externals = include_externals
            self.lineno = lineno

    def __init__(self, bdb_location_service):
        self._bdb_location_service = bdb_location_service

        self._modules = frozenset(sys.modules.values())
        self._path_cache = {}
        self._post_import_notifications = {}

        self._thread = None
        self._quit = False

        self._old_import = None

        external_paths = [sys.exec_prefix]
        if hasattr(site, 'getsitepackages'):
            external_paths = external_paths + site.getsitepackages()

        self.external_paths = [os.path.normcase(os.path.realpath(external_path))
                               for external_path in external_paths]

        if on_lambda():
            _BLACKLISTED_PATHS.append('/var/task/flask')

        import platform
        if platform.system() != 'Windows' and ImportServiceConfig.USE_IMPORT_HOOK:
            platform = platform.python_implementation().lower()

            def import_hook(*args, **kwargs):
                """
                Declared here to make it obvious that you can't replace the function by monkeypatching -
                the C extension will always reference the function set with SetImportHook.
                """
                __rookout__tracebackhide__ = True
                # Locking the global import lock here extends the section for which it is locked -
                # we don't want the import hook to be called from two threads simultaneously,
                # but the scope in which the import lock is held might only encompass the call to the original
                # __import__. The import lock is re-entrant, so it's OK for us to lock it and then for Python
                # to lock it again.
                with import_hook.import_lock:
                    result = self._old_import(*args, **kwargs)

                    try:
                        # if the recursion count is > 1,
                        # then this call to import_hook is a nested import, which means that the parent
                        # import has not finished executing its code yet, but it's already in sys.modules.
                        # if we evaluate now, we will try to place BPs in the module before it finished executing,
                        # potentially resulting in CodeNotFound.
                        if import_hook.import_lock.get_recursion_count() == 1:
                            self.evaluate_module_list()
                    except:
                        pass

                    return result
            # this must be a reentrant lock - imports can cause other imports
            import_hook.import_lock = CountingImportLock()

            if platform == "cpython":
                import native_extensions

                native_extensions.SetImportHook(import_hook)
                # atomic swap
                builtins.__import__, self._old_import = native_extensions.CallImportHookRemovingFrames, builtins.__import__
            elif platform == "pypy":
                import __pypy__
                # atomic swap
                builtins.__import__, self._old_import = __pypy__.hidden_applevel(import_hook), builtins.__import__
            else:
                # assertion should never be reached, singleton.py checks platform support
                raise AssertionError("Unsupported platform")
        else:
            self._thread = threading.Thread(target=self._query_thread,
                                            name=ImportServiceConfig.THREAD_NAME)
            self._thread.daemon = True
            self._thread.start()

    def close(self):
        if self._old_import:
            builtins.__import__ = self._old_import

        if self._thread:
            self._quit = True

            # If threading was monkey patched by gevent waiting on thread will likely throw an exception
            try:
                from gevent.monkey import is_module_patched
                if is_module_patched("threading"):
                    time.sleep(ImportServiceConfig.SYS_MODULES_QUERY_INTERVAL)
            except:
                pass

            self._thread.join()

    def register_post_import_notification(self, aug_id, name, filename, include_externals, lineno, callback, removed):
        # Normalize file path
        if filename:
            filename = os.path.normcase(os.path.normpath(filename))

        notification = self.Notification(name, filename, include_externals, lineno, callback, removed)
        # Attempt to satisfy notification using known modules
        for module_object in self._modules:

            # Get module details and check if it matches
            module_filename = self._get_module_path(module_object)

            # If module is not valid, ignore
            if not self._is_valid_module(module_object, module_filename):
                continue

            if module_filename:
                if self._does_module_match_notification(module_object.__name__, module_filename, notification, self.external_paths):
                    notification.callback(module_object)
                    return False

        # Register notification for future loads
        self._post_import_notifications[aug_id] = notification

        return True

    def remove_aug(self, aug_id):
        notification = self._post_import_notifications.pop(aug_id, None)
        if notification is None:
            return

        notification.removed()

    def clear_augs(self):
        # This does not require a lock - `notifications` may be added to or removed from in a different thread
        # while we still haven't replaced it with an empty dict(),
        # but `notifications` is just a pointer to the same dict object pointed to by
        # `_post_import_notifications`. Once we do replace `_post_import_notifications`
        # with a new dict, we can be sure that no more notifications will be added.
        # At that point, it's safe to iterate over `notifications` and remove all notifications.
        notifications = self._post_import_notifications
        self._post_import_notifications = dict()
        for notification in six.itervalues(notifications):
            notification.removed()

    def _is_valid_module(self, module_object, module_filename):
        return module_filename and os.path.splitext(module_filename)[1] in _SUPPORTED_PY_FORMATS and \
            module_object and inspect.ismodule(module_object) and hasattr(module_object, '__file__')

    def _query_thread(self):
        self._bdb_location_service.ignore_current_thread()

        while not self._quit:
            try:
                with CountingImportLock():
                    self.evaluate_module_list()
            except:
                if logger:
                    logger.exception("Error while evaluating module list")

            # time can be None if interpreter is in shutdown
            if not time:
                return
            time.sleep(ImportServiceConfig.SYS_MODULES_QUERY_INTERVAL)

    def evaluate_module_list(self):
        try:
            # Nobody is waiting for notifications
            if not self._post_import_notifications:
                return

            # No new modules
            if len(self._modules) == len(sys.modules):
                return

            # Get a fresh list
            modules = frozenset(sys.modules.values())
            # self._modules is only replaced (it's immutable - a frozenset), so there's no need to copy it here,
            # just keep a reference to the current self._modules so we don't start working on a different set
            # mid-loop
            old_modules = self._modules

            # For everybody not in the old list, check notifications
            for module in modules:
                module_filename = self._get_module_path(module)
                if module not in old_modules and self._is_valid_module(module, module_filename):
                    self._notify_of_new_module(module.__name__, module, module_filename)

            # Update the "old" list
            self._modules = modules

        except:
            logger.exception("Exception in ImportService")

    def _notify_of_new_module(self, module_name, module_object, module_filename):
        self._trigger_all_notifications_for_module(module_filename, module_name, module_object)

    def _trigger_all_notifications_for_module(self, module_filename, module_name, module):
        augs_to_remove = set()

        if module_filename:
            for aug_id, notification in six.iteritems(self._post_import_notifications.copy()):
                if self._does_module_match_notification(module_name, module_filename, notification,
                                                        self.external_paths):
                    try:
                        augs_to_remove.add(aug_id)
                        notification.callback(module)
                    except:
                        logger.exception("Error on module load callback")
        for aug_id in augs_to_remove:
            self._post_import_notifications.pop(aug_id, None)

    def _get_module_path(self, module):
        result = self._path_cache.get(module)

        if result is not None:
            return result

        if module:
            try:
                path = inspect.getsourcefile(module)
                if not path:
                    if module.__file__.endswith('.pyc'):
                        path = module.__file__.replace('.pyc', '.py')
            except:
                return None

            if path:
                result = os.path.realpath(os.path.normcase(os.path.abspath(path)))
                self._path_cache[module] = result
                return result

        return None

    @staticmethod
    def is_black_listed_path(path):
        for blacklisted_path in _BLACKLISTED_PATHS:
            if path.startswith(blacklisted_path):
                return True
        return False

    @staticmethod
    def _does_module_match_notification(module_name, module_filename, notification, external_paths):
        if not notification.include_externals:
            for external_path in external_paths:
                if module_filename.startswith(external_path):
                    return False

        if notification.module_filename and ImportService.path_contains_path(module_filename, notification.module_filename) or \
                        notification.module_name and module_name == notification.module_name and \
                        not ImportService.is_black_listed_path(module_filename):
            return True
        else:
            return False

    @staticmethod
    def _does_code_object_match_notification(code_object, notification):
        return notification.lineno in _GetLineNumbers(code_object)

    @staticmethod
    def path_contains_path(full_path, partial_path):
        if full_path.endswith(partial_path):
            return len(full_path) == len(partial_path) or full_path[-len(partial_path)-1] in ('/', '\\')
        else:
            return False
