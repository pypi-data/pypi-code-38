from celery import signals

from stackifyapm.utils import get_name_from_func
from stackifyapm.handlers.exceptions import get_exception_context


def register_exception_tracking(client):
    dispatch_uid = "stackifyapm-exc-tracking"

    def process_failure_signal(sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
        if not client:
            return

        client.capture_exception(
            exception=get_exception_context(exception, traceback)
        )

    signals.task_failure.disconnect(process_failure_signal, dispatch_uid=dispatch_uid)
    signals.task_failure.connect(process_failure_signal, weak=False, dispatch_uid=dispatch_uid)


def register_instrumentation(client):
    def begin_transaction(*args, **kwargs):
        client.begin_transaction("celery")

    def end_transaction(task_id, task, *args, **kwargs):
        name = get_name_from_func(task)
        client.end_transaction(name, kwargs.get("state", "None"))

    dispatch_uid_prerun = "stackifyapm-tracing-prerun"
    dispatch_uid_postrun = "stackifyapm-tracing-postrun"

    signals.task_prerun.disconnect(begin_transaction, dispatch_uid=dispatch_uid_prerun)
    signals.task_postrun.disconnect(end_transaction, dispatch_uid=dispatch_uid_postrun)

    signals.task_prerun.connect(begin_transaction, dispatch_uid=dispatch_uid_prerun, weak=False)
    signals.task_postrun.connect(end_transaction, dispatch_uid=dispatch_uid_postrun, weak=False)
