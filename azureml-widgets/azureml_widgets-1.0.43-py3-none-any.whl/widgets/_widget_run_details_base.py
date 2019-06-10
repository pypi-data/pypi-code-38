# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import azureml.core
from azureml.telemetry import get_diagnostics_collection_info
import threading
import traceback
import time as systime
import uuid
import os

# noinspection PyProtectedMember
from azureml.widgets._telemetry_logger import _TelemetryLogger
# noinspection PyProtectedMember
from azureml._base_sdk_common import _ClientSessionId

from . import _platform

_logger = _TelemetryLogger.get_telemetry_logger(__name__)


class _WidgetRunDetailsBase(object):
    """Base class providing common methods by widgets."""

    def __init__(self, widget_sleep_time, widget):
        self.widget_instance = widget()
        self.widget_sleep_time = widget_sleep_time
        self.settings = {}
        self.isDebug = False

    def __del__(self):
        """Destructor for the widget."""
        pass

    def show(self, render_lib=None, widget_settings=None):
        """Render widget and start thread to refresh the widget.

        :param render_lib: The library to use for rendering.
        :type render_lib: func
        :param widget_settings: The widget settings.
        :type widget_settings: object
        """
        if widget_settings is None:
            widget_settings = {}

        widget_settings = {**self._get_default_setting(), **widget_settings}

        self.settings = widget_settings

        # pass the widget settings to client
        self.widget_instance.widget_settings = self.settings
        self.isDebug = 'debug' in self.settings and self.settings['debug']

        # register events you want to subscribe to while taking actions on traitlets on client side
        try:
            self._register_events()
        except Exception as e:
            if self.isDebug:
                self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))

        _render_override = os.environ.get('AMLWIDGET_RENDER')
        _render = not _render_override or _render_override == "1"

        # render the widget
        telemetry_values = self._get_telemetry_values(self.show)
        with _TelemetryLogger.log_activity(_logger,
                                           "train.widget.show",
                                           custom_dimensions=telemetry_values):
            if _render:
                try:
                    from IPython.display import display
                    display(self.widget_instance)
                except Exception as e:
                    if render_lib is not None:
                        render_lib(self.widget_instance.get_html())
                    if self.isDebug:
                        self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))

        def _is_async():
            _sync_override_flag = os.environ.get('AMLWIDGET_SYNC')
            _sync_override = _sync_override_flag and _sync_override_flag == "1"
            return _platform._in_jupyter_nb() and not _sync_override

        # refresh the widget in given interval
        if _is_async():
            thread = threading.Thread(target=self._refresh_widget, args=(render_lib, self.settings, _render))
            thread.start()
        else:
            self._refresh_widget(render_lib, self.settings, _render)

    def _refresh_widget(self, render_lib, widget_settings, render_widget=True):
        """Retrieve data from data source and update widget data value to reflect it on UI.

        :param render_lib: The library to use for rendering.
        :type render_lib: func
        :param widget_settings: The widget settings.
        :type widget_settings: object
        """
        telemetry_values = self._get_telemetry_values(self._refresh_widget)
        with _TelemetryLogger.log_activity(_logger,
                                           "train.widget.refresh",
                                           custom_dimensions=telemetry_values) as activity_logger:
            lastError = None
            lastErrorCount = 0
            while True:
                try:
                    activity_logger.info(("Getting widget data..."))
                    widget_data = self.get_widget_data(widget_settings)
                    activity_logger.info(("Rendering the widget..."))
                    if render_lib is not None:
                        render_lib(self.widget_instance.get_html())
                    self.widget_instance.error = ''
                    if self._should_stop_refresh(widget_data):
                        activity_logger.info(("Stop auto refreshing..."))
                        self.widget_instance.is_finished = True
                        break
                except Exception as e:
                    activity_logger.exception(e)

                    # only check exception type instead of value to avoid timestamp or some dynamic content
                    if type(e) == type(lastError):
                        lastErrorCount += 1
                    else:
                        lastError = e
                        lastErrorCount = 0

                    if lastErrorCount > 2:
                        if self.isDebug:
                            self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))
                        else:
                            self.widget_instance.error = repr(traceback.format_exception_only(type(e), e))

                        if not render_widget:
                            raise
                        break

                systime.sleep(self.widget_sleep_time)

    def get_widget_data(self, widget_settings=None):
        """Abstract method for retrieving data to be rendered by widget."""
        pass

    def _should_stop_refresh(self, widget_data):
        pass

    def _register_events(self):
        pass

    def _register_event(self, callback, traitlet_name):
        self.widget_instance.observe(callback, names=traitlet_name)

    def _get_default_setting(self):
        send_telemetry, level = get_diagnostics_collection_info()
        return {"childWidgetDisplay": "popup",
                "send_telemetry": send_telemetry,
                "log_level": level,
                "sdk_version": azureml.core.VERSION}

    def _get_telemetry_values(self, func):
        telemetry_values = {}

        # client common...
        telemetry_values['amlClientType'] = 'azureml-train-widget'
        telemetry_values['amlClientFunction'] = func.__name__
        telemetry_values['amlClientModule'] = self.__class__.__module__
        telemetry_values['amlClientClass'] = self.__class__.__name__
        telemetry_values['amlClientRequestId'] = str(uuid.uuid4())
        telemetry_values['amlClientSessionId'] = _ClientSessionId

        return telemetry_values
