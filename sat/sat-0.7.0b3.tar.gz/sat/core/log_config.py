#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a XMPP client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""High level logging functions"""
# XXX: this module use standard logging module when possible, but as SàT can work in different cases where logging is not the best choice (twisted, pyjamas, etc), it is necessary to have a dedicated module. Additional feature like environment variables and colors are also managed.

from sat.core.constants import Const as C
from sat.core import log


class TwistedLogger(log.Logger):
    colors = True
    force_colors = False

    def __init__(self, *args, **kwargs):
        super(TwistedLogger, self).__init__(*args, **kwargs)
        from twisted.python import log as twisted_log

        self.twisted_log = twisted_log

    def out(self, message, level=None, **kwargs):
        """Actually log the message

        @param message: formatted message
        """
        if kwargs.get('exc_info', False):
            message = self.addTraceback(message)
        self.twisted_log.msg(
            message.encode("utf-8", "ignore"), sat_logged=True, level=level
        )


class ConfigureBasic(log.ConfigureBase):
    def configureColors(self, colors, force_colors, levels_taints_dict):
        super(ConfigureBasic, self).configureColors(
            colors, force_colors, levels_taints_dict
        )
        if colors:
            import sys

            try:
                isatty = sys.stdout.isatty()
            except AttributeError:
                isatty = False
            # FIXME: isatty should be tested on each handler, not globaly
            if (force_colors or isatty):
                # we need colors
                log.Logger.post_treat = lambda logger, level, message: self.ansiColors(
                    level, message
                )
        elif force_colors:
            raise ValueError("force_colors can't be used if colors is False")

    @staticmethod
    def getProfile():
        """Try to find profile value using introspection"""
        import inspect

        stack = inspect.stack()
        current_path = stack[0][1]
        for frame_data in stack[:-1]:
            if frame_data[1] != current_path:
                if (
                    log.backend == C.LOG_BACKEND_STANDARD
                    and "/logging/__init__.py" in frame_data[1]
                ):
                    continue
                break

        frame = frame_data[0]
        args = inspect.getargvalues(frame)
        try:
            profile = args.locals.get("profile") or args.locals["profile_key"]
        except (TypeError, KeyError):
            try:
                try:
                    profile = args.locals["self"].profile
                except AttributeError:
                    try:
                        profile = args.locals["self"].parent.profile
                    except AttributeError:
                        profile = args.locals[
                            "self"
                        ].host.profile  # used in quick_frontend for single profile configuration
            except Exception:
                # we can't find profile, we return an empty value
                profile = ""
        return profile


class ConfigureTwisted(ConfigureBasic):
    LOGGER_CLASS = TwistedLogger

    def changeObserver(self, observer, can_colors=False):
        """Install a hook on observer to manage SàT specificities

        @param observer: original observer to hook
        @param can_colors: True if observer can display ansi colors
        """

        def observer_hook(event):
            """redirect non SàT log to twisted_logger, and add colors when possible"""
            if (
                "sat_logged" in event
            ):  # we only want our own logs, other are managed by twistedObserver
                # we add colors if possible
                if (
                    can_colors and self.LOGGER_CLASS.colors
                ) or self.LOGGER_CLASS.force_colors:
                    message = event.get("message", tuple())
                    if message:
                        event["message"] = ("".join(message),)  # must be a tuple
                observer(event)  # we can now call the original observer

        return observer_hook

    def changeFileLogObserver(self, observer):
        """Install SàT hook for FileLogObserver

        if the output is a tty, we allow colors, else we don't
        @param observer: original observer to hook
        """
        log_obs = observer.__self__
        log_file = log_obs.write.__self__
        try:
            can_colors = log_file.isatty()
        except AttributeError:
            can_colors = False
        return self.changeObserver(observer, can_colors=can_colors)

    def installObserverHook(self, observer):
        """Check observer type and install SàT hook when possible

        @param observer: observer to hook
        @return: hooked observer or original one
        """
        if hasattr(observer, "__self__"):
            ori = observer
            if isinstance(observer.__self__, self.twisted_log.FileLogObserver):
                observer = self.changeFileLogObserver(observer)
            elif isinstance(observer.__self__, self.twisted_log.DefaultObserver):
                observer = self.changeObserver(observer, can_colors=True)
            else:
                # we use print because log system is not fully initialized
                print("Unmanaged observer [%s]" % observer)
                return observer
            self.observers[ori] = observer
        return observer

    def preTreatment(self):
        """initialise needed attributes, and install observers hooks"""
        self.observers = {}
        from twisted.python import log as twisted_log

        self.twisted_log = twisted_log
        self.log_publisher = twisted_log.msg.__self__

        def addObserverObserver(self_logpub, other):
            """Install hook so we know when a new observer is added"""
            other = self.installObserverHook(other)
            return self_logpub._originalAddObserver(other)

        def removeObserverObserver(self_logpub, ori):
            """removeObserver hook fix

            As we wrap the original observer, the original removeObserver may want to remove the original object instead of the wrapper, this method fix this
            """
            if ori in self.observers:
                self_logpub._originalRemoveObserver(self.observers[ori])
            else:
                try:
                    self_logpub._originalRemoveObserver(ori)
                except ValueError:
                    try:
                        ori in self.cleared_observers
                    except AttributeError:
                        raise ValueError("Unknown observer")

        # we replace addObserver/removeObserver by our own
        twisted_log.LogPublisher._originalAddObserver = (
            twisted_log.LogPublisher.addObserver
        )
        twisted_log.LogPublisher._originalRemoveObserver = (
            twisted_log.LogPublisher.removeObserver
        )
        import types  # see https://stackoverflow.com/a/4267590 (thx Chris Morgan/aaronasterling)

        twisted_log.addObserver = types.MethodType(
            addObserverObserver, self.log_publisher, twisted_log.LogPublisher
        )
        twisted_log.removeObserver = types.MethodType(
            removeObserverObserver, self.log_publisher, twisted_log.LogPublisher
        )

        # we now change existing observers
        for idx, observer in enumerate(self.log_publisher.observers):
            self.log_publisher.observers[idx] = self.installObserverHook(observer)

    def configureLevel(self, level):
        self.LOGGER_CLASS.level = level
        super(ConfigureTwisted, self).configureLevel(level)

    def configureOutput(self, output):
        import sys

        if output is None:
            output = C.LOG_OPT_OUTPUT_SEP + C.LOG_OPT_OUTPUT_DEFAULT
        self.manageOutputs(output)
        addObserver = self.twisted_log.addObserver

        if C.LOG_OPT_OUTPUT_DEFAULT in log.handlers:
            # default output is already managed, we just add output to stdout if we are in debug or nodaemon mode
            if self.backend_data is None:
                raise ValueError(
                    "You must pass options as backend_data with Twisted backend"
                )
            options = self.backend_data
            if options.get("nodaemon", False) or options.get("debug", False):
                addObserver(self.twisted_log.FileLogObserver(sys.stdout).emit)
        else:
            # \\default is not in the output, so we remove current observers
            self.cleared_observers = self.log_publisher.observers
            self.observers.clear()
            del self.log_publisher.observers[:]
            # and we forbid twistd to add any observer
            self.twisted_log.addObserver = lambda other: None

        if C.LOG_OPT_OUTPUT_FILE in log.handlers:
            from twisted.python import logfile

            for path in log.handlers[C.LOG_OPT_OUTPUT_FILE]:
                log_file = (
                    sys.stdout if path == "-" else logfile.LogFile.fromFullPath(path)
                )
                addObserver(self.twisted_log.FileLogObserver(log_file).emit)

        if C.LOG_OPT_OUTPUT_MEMORY in log.handlers:
            raise NotImplementedError(
                "Memory observer is not implemented in Twisted backend"
            )

    def configureColors(self, colors, force_colors, levels_taints_dict):
        super(ConfigureTwisted, self).configureColors(
            colors, force_colors, levels_taints_dict
        )
        self.LOGGER_CLASS.colors = colors
        self.LOGGER_CLASS.force_colors = force_colors
        if force_colors and not colors:
            raise ValueError("colors must be True if force_colors is True")

    def postTreatment(self):
        """Install twistedObserver which manage non SàT logs"""

        def twistedObserver(event):
            """Observer which redirect log message not produced by SàT to SàT logging system"""
            if not "sat_logged" in event:
                # this log was not produced by SàT
                from twisted.python import log as twisted_log

                text = twisted_log.textFromEventDict(event)
                if text is None:
                    return
                twisted_logger = log.getLogger(C.LOG_TWISTED_LOGGER)
                log_method = (
                    twisted_logger.error
                    if event.get("isError", False)
                    else twisted_logger.info
                )
                log_method(text.decode("utf-8"))

        self.log_publisher._originalAddObserver(twistedObserver)


class ConfigureStandard(ConfigureBasic):
    def __init__(
        self,
        level=None,
        fmt=None,
        output=None,
        logger=None,
        colors=False,
        levels_taints_dict=None,
        force_colors=False,
        backend_data=None,
    ):
        if fmt is None:
            fmt = C.LOG_OPT_FORMAT[1]
        if output is None:
            output = C.LOG_OPT_OUTPUT[1]
        super(ConfigureStandard, self).__init__(
            level,
            fmt,
            output,
            logger,
            colors,
            levels_taints_dict,
            force_colors,
            backend_data,
        )

    def preTreatment(self):
        """We use logging methods directly, instead of using Logger"""
        import logging

        log.getLogger = logging.getLogger
        log.debug = logging.debug
        log.info = logging.info
        log.warning = logging.warning
        log.error = logging.error
        log.critical = logging.critical

    def configureLevel(self, level):
        if level is None:
            level = C.LOG_LVL_DEBUG
        self.level = level

    def configureFormat(self, fmt):
        super(ConfigureStandard, self).configureFormat(fmt)
        import logging
        import sys

        class SatFormatter(logging.Formatter):
            u"""Formatter which manage SàT specificities"""
            _format = fmt
            _with_profile = "%(profile)s" in fmt

            def __init__(self, can_colors=False):
                super(SatFormatter, self).__init__(self._format)
                self.can_colors = can_colors

            def format(self, record):
                if self._with_profile:
                    record.profile = ConfigureStandard.getProfile()
                do_color = self.with_colors and (self.can_colors or self.force_colors)
                if ConfigureStandard._color_location:
                    # we copy raw formatting strings for color_*
                    # as formatting is handled in ansiColors in this case
                    if do_color:
                        record.color_start = log.COLOR_START
                        record.color_end = log.COLOR_END
                    else:
                        record.color_start = record.color_end = ""
                s = super(SatFormatter, self).format(record)
                if do_color:
                    s = ConfigureStandard.ansiColors(record.levelname, s)
                if sys.platform == "android":
                    # FIXME: dirty hack to workaround android encoding issue on log
                    #        need to be fixed properly
                    return s.encode("ascii", "ignore")
                else:
                    return s

        self.formatterClass = SatFormatter

    def configureOutput(self, output):
        self.manageOutputs(output)

    def configureLogger(self, logger):
        self.name_filter = log.FilterName(logger) if logger else None

    def configureColors(self, colors, force_colors, levels_taints_dict):
        super(ConfigureStandard, self).configureColors(
            colors, force_colors, levels_taints_dict
        )
        self.formatterClass.with_colors = colors
        self.formatterClass.force_colors = force_colors
        if not colors and force_colors:
            raise ValueError("force_colors can't be used if colors is False")

    def _addHandler(self, root_logger, hdlr, can_colors=False):
        hdlr.setFormatter(self.formatterClass(can_colors))
        root_logger.addHandler(hdlr)
        root_logger.setLevel(self.level)
        if self.name_filter is not None:
            hdlr.addFilter(self.name_filter)

    def postTreatment(self):
        import logging

        root_logger = logging.getLogger()
        if len(root_logger.handlers) == 0:
            for handler, options in log.handlers.items():
                if handler == C.LOG_OPT_OUTPUT_DEFAULT:
                    hdlr = logging.StreamHandler()
                    try:
                        can_colors = hdlr.stream.isatty()
                    except AttributeError:
                        can_colors = False
                    self._addHandler(root_logger, hdlr, can_colors=can_colors)
                elif handler == C.LOG_OPT_OUTPUT_MEMORY:
                    from logging.handlers import BufferingHandler

                    class SatMemoryHandler(BufferingHandler):
                        def emit(self, record):
                            super(SatMemoryHandler, self).emit(self.format(record))

                    hdlr = SatMemoryHandler(options)
                    log.handlers[
                        handler
                    ] = (
                        hdlr
                    )  # we keep a reference to the handler to read the buffer later
                    self._addHandler(root_logger, hdlr, can_colors=False)
                elif handler == C.LOG_OPT_OUTPUT_FILE:
                    import os.path

                    for path in options:
                        hdlr = logging.FileHandler(os.path.expanduser(path))
                        self._addHandler(root_logger, hdlr, can_colors=False)
                else:
                    raise ValueError("Unknown handler type")
        else:
            root_logger.warning(u"Handlers already set on root logger")

    @staticmethod
    def memoryGet(size=None):
        """Return buffered logs

        @param size: number of logs to return
        """
        mem_handler = log.handlers[C.LOG_OPT_OUTPUT_MEMORY]
        return (
            log_msg for log_msg in mem_handler.buffer[size if size is None else -size :]
        )


log.configure_cls[C.LOG_BACKEND_BASIC] = ConfigureBasic
log.configure_cls[C.LOG_BACKEND_TWISTED] = ConfigureTwisted
log.configure_cls[C.LOG_BACKEND_STANDARD] = ConfigureStandard


def configure(backend, **options):
    """Configure logging behaviour
    @param backend: can be:
        C.LOG_BACKEND_STANDARD: use standard logging module
        C.LOG_BACKEND_TWISTED: use twisted logging module (with standard logging observer)
        C.LOG_BACKEND_BASIC: use a basic print based logging
        C.LOG_BACKEND_CUSTOM: use a given Logger subclass
    """
    return log.configure(backend, **options)


def _parseOptions(options):
    """Parse string options as given in conf or environment variable, and return expected python value

    @param options (dict): options with (key: name, value: string value)
    """
    COLORS = C.LOG_OPT_COLORS[0]
    LEVEL = C.LOG_OPT_LEVEL[0]

    if COLORS in options:
        if options[COLORS].lower() in ("1", "true"):
            options[COLORS] = True
        elif options[COLORS] == "force":
            options[COLORS] = True
            options["force_colors"] = True
        else:
            options[COLORS] = False
    if LEVEL in options:
        level = options[LEVEL].upper()
        if level not in C.LOG_LEVELS:
            level = C.LOG_LVL_INFO
        options[LEVEL] = level


def satConfigure(backend=C.LOG_BACKEND_STANDARD, const=None, backend_data=None):
    """Configure logging system for SàT, can be used by frontends

    logs conf is read in SàT conf, then in environment variables. It must be done before Memory init
    @param backend: backend to use, it can be:
        - C.LOG_BACKEND_BASIC: print based backend
        - C.LOG_BACKEND_TWISTED: Twisted logging backend
        - C.LOG_BACKEND_STANDARD: standard logging backend
    @param const: Const class to use instead of sat.core.constants.Const (mainly used to change default values)
    """
    if const is not None:
        global C
        C = const
        log.C = const
    from sat.tools import config
    import os

    log_conf = {}
    sat_conf = config.parseMainConf()
    for opt_name, opt_default in C.LOG_OPTIONS():
        try:
            log_conf[opt_name] = os.environ[
                "".join((C.ENV_PREFIX, C.LOG_OPT_PREFIX.upper(), opt_name.upper()))
            ]
        except KeyError:
            log_conf[opt_name] = config.getConfig(
                sat_conf, C.LOG_OPT_SECTION, C.LOG_OPT_PREFIX + opt_name, opt_default
            )

    _parseOptions(log_conf)
    configure(backend, backend_data=backend_data, **log_conf)
