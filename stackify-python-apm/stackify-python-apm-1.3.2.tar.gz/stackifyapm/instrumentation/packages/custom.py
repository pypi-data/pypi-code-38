import json
import logging
import os
import sys

from stackifyapm.handlers.exceptions import get_exception_context
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils.helper import is_async_span
from stackifyapm.traces import get_transaction


logger = logging.getLogger(__name__)


class CustomInstrumentation(AbstractInstrumentedModule):
    """
    Custom instrumentation support
    to be able to let user do custom instrumentation without code changes,
    we provide this custom instrumenation module to instrument
    specific class method provider by the user in their config file
    """
    name = "custom_instrumentation"
    instrumentations = []
    instrument_list = []

    def get_instrument_list(self):
        self.instrument_list = []
        config_file = self.client and self.client.get_application_info().get('config_file')

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file) as json_file:
                    data = json.load(json_file)
                    self.instrumentations = data.get('instrumentation', [])

                    for instrumentation in self.instrumentations:
                        class_name = instrumentation.get('class')
                        method_name = instrumentation.get('method')
                        method = class_name and "{}.{}".format(class_name, method_name) or method_name
                        self.instrument_list.append((instrumentation.get('module'), method))

            except Exception:
                logger.warning('Unable to read stackify json file.')

        return self.instrument_list

    def call(self, module, method, wrapped, instance, args, kwargs):
        class_name, method_name = method.split('.')
        instrumentations = [i for i in self.instrumentations if i.get('class') == class_name and i.get('method') == method_name]
        custom_type = 'custom.{}.{}'.format(class_name, method_name)

        if instrumentations:
            instrumentation = instrumentations[0]

            if instrumentation.get('transaction') and self.client and not get_transaction():
                self.client.begin_transaction('custom', client=self.client)
                try:
                    call = wrapped(*args, **kwargs)
                except Exception:
                    exc_info = sys.exc_info()
                    self.client.capture_exception(
                        exception=get_exception_context(exc_info[1], exc_info[2])
                    )
                    self.client.end_transaction(name=custom_type)
                    raise

                self.client.end_transaction(name=custom_type)
                return call
            else:
                extra_data = {
                    "type": "Python",
                }
                extra_data.update(instrumentation.get('extra', {}))

                if instrumentation.get('trackedFunction'):
                    extra_data['tracked_func'] = instrumentation.get('trackedFunctionName', '{ClassName}.{MethodName}').format(
                        ClassName=class_name,
                        MethodName=method_name,
                    )

                with CaptureSpan('custom', custom_type, extra_data, leaf=False, is_async=is_async_span()):
                    return wrapped(*args, **kwargs)

        return wrapped(*args, **kwargs)
