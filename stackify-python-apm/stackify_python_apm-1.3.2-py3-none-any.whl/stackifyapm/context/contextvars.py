from __future__ import absolute_import

import contextvars

stackifyapm_transaction_var = contextvars.ContextVar("stackifyapm_transaction_var")
stackifyapm_span_var = contextvars.ContextVar("stackifyapm_span_var")


def get_transaction(clear=False):
    try:
        transaction = stackifyapm_transaction_var.get()
        if clear:
            set_transaction(None)
        return transaction
    except LookupError:
        return None


def set_transaction(transaction):
    stackifyapm_transaction_var.set(transaction)


def get_span():
    try:
        return stackifyapm_span_var.get()
    except LookupError:
        return None


def set_span(span):
    stackifyapm_span_var.set(span)


def clear_span():
    set_span(None)
