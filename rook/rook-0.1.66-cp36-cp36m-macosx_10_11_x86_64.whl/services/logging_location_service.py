import logging
import six
import inspect
import os
import threading

from rook.logger import logger

from rook.processor.namespaces.container_namespace import ContainerNamespace
from rook.processor.namespaces.frame_namespace import FrameNamespace
from rook.augs.processor_extensions.namespaces.log_record_namespace import LogRecordNamespace


class LoggingLocationService(object):

    NAME = "logging"

    class Handler(logging.Handler):

        def __init__(self, logger):
            super(LoggingLocationService.Handler, self).__init__()

            self._name = logger.name

            self._logger = logger
            self._old_remove_handler = self._logger.removeHandler

            # Do not allow us to be removed
            def removeHandler(handler):
                if handler != self:
                    self._old_remove_handler(handler)
            self._logger.removeHandler = removeHandler

            self._logger.addHandler(self)

            self._augs = {}
            self._lock = threading.RLock()

        def close(self):
            self._logger.removeHandler = self._old_remove_handler
            self._logger.removeHandler(self)

        def emit(self, record):
            try:
                frame = FrameNamespace(self._get_frame(record))
                extracted = ContainerNamespace({'log_record': LogRecordNamespace(record)})

                with self._lock:
                    for aug in six.itervalues(self._augs):
                        aug.execute(frame, extracted)
            except:
                logger.exception("Error while processing log record")

        def add_aug(self, aug):
            with self._lock:
                self._augs[aug.aug_id] = aug

                aug.set_active()

        def remove_aug(self, aug_id):
            with self._lock:
                try:
                    aug = self._augs[aug_id]
                except KeyError:
                    return

                del self._augs[aug_id]
                aug.set_removed()

        def clear_augs(self):
            with self._lock:
                aug_ids = list(self._augs.keys())

                for aug_id in aug_ids:
                    self.remove_aug(aug_id)

        def empty(self):
            return len(self._augs) == 0

        def _get_frame(self, record):
            # Skip the top two frames (ours)
            frame = inspect.currentframe().f_back.f_back

            while hasattr(frame, "f_code"):
                filename = os.path.normcase(frame.f_code.co_filename)
                if filename == logging._srcfile:
                    frame = frame.f_back
                else:
                    return frame

            return None

    def __init__(self):
        self._hooked = False

        self._handlers = dict()
        self.rootHandler = None
        self._lock = threading.RLock()

    def add_logging_aug(self, name, aug):
        with self._lock:
            self._installHooks()

            try:
                handler = self._handlers[name]
            except KeyError:
                logger = logging.getLogger(name)
                handler = self.Handler(logger)
                self._handlers[name] = handler

                # We document root handler for basicConfig support
                if logger == logging.root:
                    self.rootHandler = handler

        handler.add_aug(aug)

    def remove_aug(self, aug_id):
        with self._lock:
            for handler in six.itervalues(self._handlers):
                handler.remove_aug(aug_id)

        self.prune_handlers()

    def clear_augs(self):
        with self._lock:
            for handler in six.itervalues(self._handlers):
                handler.clear_augs()

        self.prune_handlers()

    def prune_handlers(self):
        with self._lock:
            loggers_to_prune = [logger for logger, handler in six.iteritems(self._handlers) if handler.empty()]

            for logger in loggers_to_prune:

                self._handlers[logger].close()

                # If we just closed rootHandler, remove it
                if self._handlers[logger] == self.rootHandler:
                    self.rootHandler = None

                del self._handlers[logger]

    def close(self):
        self.clear_augs()

    def _installHooks(self):
        with self._lock:
            if self._hooked:
                return

            self.originalBasicConfig = logging.basicConfig
            logging.basicConfig = self._basicConfigHook

            for name in ["critical", "error", "warning", "info", "debug", "log"]:
                self._wrap_logging_method(name)

            self._hooked = True

    def _basicConfigHook(self, **kwargs):
        logging._acquireLock()

        try:
            if self.rootHandler:
                self.rootHandler._old_remove_handler(self.rootHandler)

                try:
                    self.originalBasicConfig(**kwargs)
                finally:
                    logging.root.addHandler(self.rootHandler)

            else:
                self.originalBasicConfig(**kwargs)
        finally:
            logging._releaseLock()

    def _isBasicConfigNeeded(self):
        return len(logging.root.handlers) == 0 or (len(logging.root.handlers) == 1 and self.rootHandler)

    # based off https://github.com/getsentry/raven-python/blob/master/raven/breadcrumbs.py
    def _wrap_logging_method(self, name):

        func = logging.__dict__[name]
        code = func.__code__

        logging_srcfile = logging._srcfile
        if logging_srcfile is None:
            logging_srcfile = os.path.normpath(
                logging.currentframe.__code__.co_filename
            )

        # This requires a bit of explanation why we're doing this.  Due to how
        # logging itself works we need to pretend that the method actually was
        # created within the logging module.  There are a few ways to detect
        # this and we fake all of them: we use the same function globals (the
        # one from the logging module), we create it entirely there which
        # means that also the filename is set correctly.  This fools the
        # detection code in logging and it makes logging itself skip past our
        # code when determining the code location.
        #
        # Because we point the globals to the logging module we now need to
        # refer to our own functions (original and the crumb recording
        # function) through a closure instead of the global scope.
        #
        # We also add a lot of newlines in front of the code so that the
        # code location lines up again in case someone runs inspect.getsource
        # on the function.
        ns = {}
        eval(compile('''%(offset)sif 1:
        def factory(name, isBasicConfigNeeded):
            def %(name)s(*args, **kwargs):
                if isBasicConfigNeeded():
                    basicConfig()
                
                return getattr(root, name)(*args, **kwargs)
            return %(name)s
        \n''' % {
            'offset': '\n' * (code.co_firstlineno - 3),
            'name': name,
        }, logging_srcfile, 'exec'), logging.__dict__, ns)

        new_func = ns['factory'](name, self._isBasicConfigNeeded)
        new_func.__doc__ = func.__doc__

        assert code.co_firstlineno == code.co_firstlineno

        # In theory this should already be set correctly, but in some cases
        # it is not.  So override it.
        new_func.__module__ = func.__module__
        new_func.__name__ = func.__name__

        logging.__dict__[name] = new_func

