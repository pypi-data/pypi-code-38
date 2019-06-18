import threading

thread_local = threading.local()
thread_local.transaction = None
stackifyapm_span_var = None


def get_transaction(clear=False):
    """
    Get the transaction for the current thread.
    """
    transaction = getattr(thread_local, "transaction", None)
    if clear:
        set_transaction(None)
    return transaction


def set_transaction(transaction):
    thread_local.transaction = transaction


def get_span():
    return getattr(thread_local, "span", None)


def set_span(span):
    thread_local.span = span


def clear_span():
    set_span(None)
