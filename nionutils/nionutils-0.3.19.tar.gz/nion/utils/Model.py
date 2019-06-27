"""
    Model classes. Useful for bindings.
"""

# standard libraries
import asyncio
import concurrent.futures
import operator
import threading

# third party libraries
# none

# local libraries
from . import Event
from . import Observable
from . import Stream


class PropertyModel(Observable.Observable):

    """
        Holds a value which can be observed for changes. The value can be any type that supports equality test.

        An optional on_value_changed method gets called when the value changes.
    """

    def __init__(self, value=None, cmp=None):
        super(PropertyModel, self).__init__()
        self.__value = value
        self.__cmp = cmp if cmp else operator.eq
        self.on_value_changed = None

    def close(self):
        self.on_value_changed = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self.__value is None:
            not_equal = value is not None
        elif value is None:
            not_equal = self.__value is not None
        else:
            not_equal = not self.__cmp(value, self.__value)
        if not_equal:
            self.__value = value
            self.notify_property_changed("value")
            if self.on_value_changed:
                self.on_value_changed(value)


class FuncStreamValueModel(PropertyModel):
    """Converts a stream of functions to a property model, evaluated asynchronously, on a thread."""

    def __init__(self, value_func_stream: Stream.AbstractStream, event_loop: asyncio.AbstractEventLoop, value=None, cmp=None):
        super().__init__(value=value, cmp=cmp)
        self.__value_func_stream = value_func_stream.add_ref()
        self.__event_loop = event_loop
        self.__count = 0

        def handle_value_func(value_func):
            async def update_value():
                value_ref = [None]
                def eval(value_ref):
                    value_ref[0] = value_func()
                await event_loop.run_in_executor(None, eval, value_ref)
                value = value_ref[0]
                self.value = value
                self.notify_property_changed("value")
                self.__count -= 1
            self.__count += 1
            event_loop.create_task(update_value())

        self.__stream_listener = value_func_stream.value_stream.listen(handle_value_func)
        handle_value_func(self.__value_func_stream.value)

    def close(self):
        self.__stream_listener.close()
        self.__stream_listener = None
        self.__value_func_stream.remove_ref()
        self.__value_func_stream = None
        self.__event_loop = None
        super().close()

    def _run_until_complete(self):
        while self.__count > 0:
            self.__event_loop.stop()
            self.__event_loop.run_forever()

    def _evaluate_immediate(self):
        return self.__value_func_stream.value()


class StreamValueModel(PropertyModel):
    """Converts a stream to a property model."""

    def __init__(self, value_stream: Stream.AbstractStream, value=None, cmp=None):
        super().__init__(value=value, cmp=cmp)
        self.__value_stream = value_stream.add_ref()

        def handle_value(value):
            self.value = value

        self.__stream_listener = value_stream.value_stream.listen(handle_value)

        handle_value(value_stream.value)

    def close(self):
        self.__stream_listener.close()
        self.__stream_listener = None
        self.__value_stream.remove_ref()
        self.__value_stream = None
        super().close()
