import functools
import logging
import multiprocessing
import os
import threading

from stackifyapm.traces import get_transaction
from stackifyapm.traces import set_transaction
from stackifyapm.traces import set_span
from stackifyapm.utils import wrapt

logger = logging.getLogger("stackifyapm.instrument")


class AbstractInstrumentedModule(object):
    client = None
    name = None
    mutates_unsampled_arguments = False

    instrument_list = []

    def __init__(self):
        self.originals = {}
        self.instrumented = False

        assert self.name is not None

    def get_wrapped_name(self, wrapped, instance, fallback_method=None):
        wrapped_name = []
        if hasattr(instance, "__class__") and hasattr(instance.__class__, "__name__"):
            wrapped_name.append(instance.__class__.__name__)

        if hasattr(wrapped, "__name__"):
            wrapped_name.append(wrapped.__name__)
        elif fallback_method:
            attribute = fallback_method.split(".")
            if len(attribute) == 2:
                wrapped_name.append(attribute[1])

        return ".".join(wrapped_name)

    def get_instrument_list(self):
        return self.instrument_list

    def instrument(self, client=None):
        self.client = client or self.client

        if self.instrumented:
            return

        skip_env_var = "SKIP_INSTRUMENT_" + str(self.name.upper())
        if skip_env_var in os.environ:
            logger.debug("Skipping instrumentation of {}. {} is set.".format(self.name, skip_env_var))
            return
        try:
            instrument_list = self.get_instrument_list()
            skipped_modules = set()
            instrumented_methods = []

            for module, method in instrument_list:
                try:
                    if module in skipped_modules:  # skip failed modules
                        continue

                    parent, attribute, original = wrapt.resolve_path(module, method)
                    self.originals[(module, method)] = original
                    wrapper = wrapt.FunctionWrapper(original, functools.partial(self.call_if_sampling, module, method))
                    wrapt.apply_patch(parent, attribute, wrapper)
                    instrumented_methods.append((module, method))
                except ImportError:
                    logger.debug("Skipping instrumentation of {}. Module {} not found".format(self.name, module))
                    skipped_modules.add(module)
                except AttributeError as ex:
                    logger.debug("Skipping instrumentation of {}.{}: {}".format(module, method, ex))

            if instrumented_methods:
                logger.debug("Instrumented {}, {}".format(self.name, ", ".join(".".join(m) for m in instrumented_methods)))

        except ImportError as ex:
            logger.debug("Skipping instrumentation of {}. {}".format(self.name, ex))
        self.instrumented = True

    def uninstrument(self, client=None):
        self.client = client or self.client

        if not self.instrumented or not self.originals:
            return

        uninstrumented_methods = []
        for module, method in self.get_instrument_list():
            if (module, method) in self.originals:
                parent, attribute, wrapper = wrapt.resolve_path(module, method)
                wrapt.apply_patch(parent, attribute, self.originals[(module, method)])
                uninstrumented_methods.append((module, method))

        if uninstrumented_methods:
            logger.debug("Uninstrumented {}, {}".format(self.name, ", ".join(".".join(m) for m in uninstrumented_methods)))

        self.instrumented = False
        self.originals = {}

    def call_if_sampling(self, module, method, wrapped, instance, args, kwargs):
        transaction = get_transaction()
        if not transaction:
            thread = threading.current_thread()
            process = multiprocessing.current_process()

            if hasattr(thread, 'transaction'):
                set_transaction(thread.transaction)
                transaction = thread.transaction
            if hasattr(thread, 'span'):
                set_span(thread.span)

            if hasattr(process, 'transaction'):
                set_transaction(process.transaction)
                transaction = process.transaction
            if hasattr(process, 'span'):
                set_span(process.span)

        if (not transaction or not transaction.get_is_sampled()) and self.name not in ["custom_instrumentation"]:
            return wrapped(*args, **kwargs)
        else:
            return self.call(module, method, wrapped, instance, args, kwargs)

    def call(self, module, method, wrapped, instance, args, kwargs):
        raise NotImplementedError
