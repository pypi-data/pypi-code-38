import json
import logging
import os
from functools import wraps
from traceback import extract_tb

import requests
from totec import JobStatus

log = logging.getLogger(__name__)


class DataError(Exception):
    def __init__(self, message=None, cause=None):
        super().__init__(message or str(cause))
        self._cause = cause

    def to_dict(self):
        if hasattr(self._cause, "to_dict"):
            return self._cause.to_dict()
        return {"message": str(self)}


class JobListener:
    def __init__(self, backend, queue_names, outputs_encoder=None):
        self._backend = backend
        self._queue_names = queue_names
        self._outputs_encoder = outputs_encoder or json.JSONEncoder

    def handle(self, dispatch):
        log.info("Listening on queues %s", self._queue_names)
        for (handle, queue_name, job) in self._backend.listen(self._queue_names):

            tag = job["tag"]
            job_type = job["type"]
            inputs = job["inputs"]

            fn = dispatch.get(job_type)
            if fn is None:
                log.warning("Unable to process job %s of type %s", tag, job_type)
                continue

            log.info("Dispatching job %s from queue %s", tag, queue_name)
            try:
                outputs = fn(inputs)
                self._maybe_update_job_resource(
                    job, {"status": JobStatus.SUCCES.name, "data": outputs}
                )
                self._backend.sign_off(handle)
            # pylint: disable=broad-except
            except DataError as exc:
                log.error("Incorrect input for job %s: %s (%s)", job_type, inputs, exc)
                self._maybe_update_job_resource(
                    job,
                    {
                        "status": JobStatus.FAILED.name,
                        "data": _summarize_exception(exc),
                    },
                )
                self._backend.sign_off(handle)

    # IMPROVE: this should ideally retry (in a separate thread of control, think 2PC)
    def _maybe_update_job_resource(self, job, obj):

        body = json.dumps(obj, cls=self._outputs_encoder)
        headers = {"Content-Type": "application/json"}

        url = job.get("meta", {}).get("self")
        if url is not None:
            response = requests.patch(url, data=body, headers=headers)
            if not _success(response):
                log.warning("Failed to update resource %s: %s", url, response.text)
            log.info("Updated resource %s", url)


def _success(response):
    return response.status_code // 100 == 2


def map_exceptions(_mapping=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (ValueError, ZeroDivisionError) as exc:
                raise DataError(cause=exc)

        return wrapped

    return decorator


def _summarize_exception(exc):
    summary = {"message": str(exc)}
    if hasattr(exc, "__traceback__"):
        tb = []
        for frame_summary in extract_tb(exc.__traceback__):
            tb.append(
                {
                    "lineno": frame_summary.lineno,
                    "line": frame_summary.line,
                    "filename": os.path.basename(frame_summary.filename),
                }
            )
        summary["traceback"] = tb
    return summary
