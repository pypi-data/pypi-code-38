import sys
import os
import logging
import platform

PLATFORM = sys.platform
CPYTHON = platform.python_implementation() == 'CPython'


class DummyExtension(object): pass


if PLATFORM in ('darwin', 'linux2', 'linux'):
    hook_installed = False
    original_os_fork = os.fork

    if CPYTHON:
        import native_extensions
    else:
        native_extensions = DummyExtension()

    native_extensions.python_fork_handler_called = 1

    def os_fork_hook():
        try:
            from .singleton import singleton_obj
            singleton_obj._agent_com.stop(final=False)

        except:
            pass

        # Set "called" flag, to be checked in the
        # pthread_atfork, and reset after
        native_extensions.python_fork_handler_called = 1
        pid = original_os_fork()
        native_extensions.python_fork_handler_called = 0

        try:
            from .singleton import singleton_obj

            if pid == 0:
                # child

                # remove all log handlers since they lock
                for handler in logging.getLogger("rook").handlers:
                    logging.getLogger("rook").removeHandler(handler)

                # don't leave child with patches
                singleton_obj._agent_com._aug_manager._trigger_services.clear_augs()

                # restore original fork
                os.fork = original_os_fork
            else:
                # parent
                singleton_obj._agent_com.connect_to_agent()
        except:
            pass

        return pid

    def install_fork_handler():
        global hook_installed, original_os_fork

        if hook_installed:
            return

        if CPYTHON:
            # due to occasional deadlocks in PyPy, pthread_atfork
            # functionality is disabled
            native_extensions.RegisterPreforkCallback()

        hook_installed = True
        os.fork = os_fork_hook

else:
    def install_fork_handler():
        pass
