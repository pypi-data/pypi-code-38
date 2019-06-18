import threading

from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import get_transaction, get_span, set_transaction, set_span


def wrap_target(function, args, transaction=None, span=None):
    thread = threading.current_thread()
    thread.transaction = transaction
    thread.span = span
    transaction and set_transaction(transaction)
    span and set_span(span)
    return function(*args)


class ThreadInstrumentation(AbstractInstrumentedModule):
    name = "thread"

    instrument_list = [
        ("threading", "Thread.start"),
        ("thread", "start_new_thread"),
        ("_thread", "start_new_thread"),
        ("multiprocessing", "Process.start"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        transaction = get_transaction()

        if transaction:
            transaction.set_has_async_spans(True)
            span = get_span()

            if method == 'start_new_thread':
                args = (wrap_target, args, {'transaction': transaction, 'span': span})
            elif method == 'Thread.start':
                instance.transaction = transaction
                instance.span = span
            elif method == 'Process.start':
                instance.transaction = transaction
                instance.span = span

        return wrapped(*args, **kwargs)
