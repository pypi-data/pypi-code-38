import logging

from totec.job import JobStatus

log = logging.getLogger(__name__)


class JobClient:
    def __init__(self, store, backend, url_template, queue_template):
        self.store = store
        self._backend = backend
        self._url_template = url_template
        self._queue_template = queue_template
        log.info("Created %s", self)

    def submit(self, queue_name, job):
        self.store.put(job)

        data = self._enrich_job(job)
        # Job needs to have SUBMITTED status before worker responds
        job.transition(JobStatus.SUBMITTED)
        self.store.put(job)
        queue_name = self._queue_template.format(queue_name=queue_name)
        try:
            self._backend.push(queue_name, data)
        except Exception as exc:
            job.transition(JobStatus.SUBMIT_FAILED)
            log.error("Failed to submit job %s to %s", job.tag, self._backend)
            raise exc
        return data

    def _enrich_job(self, job):
        data = job.to_dict()
        meta = data.get("meta", {})
        meta["self"] = self._url_template.format(tag=job.tag)
        data["meta"] = meta
        return data

    def __repr__(self):
        return "<{}(url_template={}, queue_template={}, backend={})>".format(
            self.__class__.__name__,
            self._url_template,
            self._queue_template,
            self._backend.__class__.__name__,
        )
