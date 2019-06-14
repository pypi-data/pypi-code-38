import weakref
from uuid import uuid4

from tracuni.define.const import (
    CONTEXT_UID_NAME,
)
from tracuni.misc.select_coroutine import tornado_decorator
if tornado_decorator:
    from tracuni.misc.select_coroutine import (
        run_with_stack_context,
        StackContext,
    )


class Context(object):
    class Data(object):
        def __init__(self, data_dict=None):
            self.data_dict = data_dict or None

        def __eq__(self, other):

            return self.data_dict is not None \
                and other.data_dict is not None \
                and self.data_dict.get(CONTEXT_UID_NAME) is not None \
                and other.data_dict.get(CONTEXT_UID_NAME) is not None \
                and self.data_dict.get(CONTEXT_UID_NAME)\
                ==\
                other.data_dict.get(CONTEXT_UID_NAME)

    _data = Data(data_dict={})
    _instances_registry = []

    def __init__(self, *args, **kwargs):
        self.current_data = Context.Data(*args, **kwargs)
        Context._instances_registry.append(weakref.proxy(self.current_data))
        self.old_data = None

    def __enter__(self):
        if Context._data == self.current_data:
            return

        self.old_context_data = Context.Data(
            data_dict=Context._data.data_dict,
        )

        Context._data = self.current_data

    def __exit__(self, exc_type, exc_value, traceback):
        if self.old_data is not None:
            Context._data = self.old_data

        remove = set()
        for index, proxy in enumerate(Context._instances_registry):
            try:
                bool(proxy)
            except ReferenceError:
                remove.add(index)

        Context._instances_registry = [
            p
            for i, p in enumerate(Context._instances_registry)
            if i not in remove
        ]

    @classmethod
    def get_data(cls):
        return cls._data.data_dict


class ContextAccessor:
    @staticmethod
    def get(key):
        data_dict = Context.get_data()
        if data_dict is None:
            data_dict = {}
        return data_dict.get(key)

    @staticmethod
    def set(key, value):
        data_dict = Context.get_data()
        data_dict.setdefault(key, value)

    # noinspection PyDeprecation
    @staticmethod
    @tornado_decorator
    def run_root_with_context(coro):

        initial_context_data = {
            CONTEXT_UID_NAME: uuid4().hex,
        }

        def create_tornado_context():
            return Context(initial_context_data)

        result = yield run_with_stack_context(
            StackContext(create_tornado_context),
            lambda: coro()
        )

        return result


context_accessor = ContextAccessor()
