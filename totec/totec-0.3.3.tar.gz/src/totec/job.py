from datetime import datetime as dt
import logging
import uuid
from abc import ABC, abstractmethod
import enum

log = logging.getLogger(__name__)


class SimpleJob:
    """Class to describe a job.  From an instance of this class an appropriate
    worker should be able to infer which computation (i.e., which job, and which
    inputs) it should run to get the outputs.
    """

    def __init__(self, job_type, tag, status, inputs):
        """Create an instance.

        :param job_type: An identifier string indicating the type of the job to
            create.  This identifier is shared between the creator of the job
            and the workers.
        :param tag: The identifier string for the job.  Should be unique for
            jobs created at the same :class:`JobClient`.
        :param status: The initial :class:`JobStatus` of the job
        :param inputs: The inputs for the job.  It is up to the client that the
            inputs are correct for the job type.
        """
        self.tag = tag
        self.transitions = []
        self.inputs = inputs
        self.job_type = job_type
        self.status = status
        self.outputs = None

    @property
    def status(self):
        """Return the status."""
        return self.transitions[-1][0]

    @status.setter
    def status(self, status):
        """Set the status of the job.

        :param status: The new status, should be an instance of
            :class:`JobStatus`

        :raises ValueError: If the transition from the old to the new status
            is not allowed.
        """
        self.transitions.append((status, dt.utcnow()))

    @classmethod
    def create(cls, job_type, inputs):
        """Create a new job, with initial status :class:`JobStatus.CREATED`.

        See :meth:`SimpleJob.__init__`
        """
        tag = str(uuid.uuid4())
        return cls(job_type, tag, JobStatus.CREATED, inputs)

    def to_dict(self):
        """Create a JSON serializable representation of the job."""
        obj = {
            "inputs": self.inputs,
            "type": self.job_type,
            "tag": self.tag,
            "transitions": [
                (status.name, t.isoformat()) for (status, t) in self.transitions
            ],
        }
        if self.outputs is not None:
            obj["outputs"] = self.outputs
        return obj

    def transition(self, status, data=None):
        """Update the job's status.

        :param status: The new status of the job.
        :param data: The data involved in the state transition, if any.  This is
            usually either the outputs of the job for status
            :class:`JobStatus.SUCCES`, or a description of the failure for a
            failure state such as :class:`JobStatus.FAILED`.

        :returns: None
        """

        if (self.status, status) in _ALLOWED_TRANSITIONS:
            log.info(
                "Transitioning job %s from %s to %s", self.tag, self.status, status
            )
            self.status = status
            self.outputs = data
        else:
            raise ValueError(
                "Cannot transition from {} to {}".format(self.status, status)
            )

    def __repr__(self):
        return "<{}(tag={}, status={})>".format(
            self.__class__.__name__, self.tag, self.status
        )


class JobStatus(enum.Enum):
    CREATED = 0x01
    SUBMITTED = 0x02
    SUBMIT_FAILED = 0x04
    SUCCES = 0x08
    FAILED = 0x10

    def __repr__(self):
        return self.name

    @property
    def code(self):
        return self.name

    def __str__(self):
        return repr(self)

    @classmethod
    def from_code(cls, s):
        return cls.from_string(s)

    @classmethod
    def from_string(cls, s):
        for value in cls:
            if value.name == s:
                return value
        raise ValueError("{} not a valid {}".format(s, cls.__name__))


# yapf: disable
_ALLOWED_TRANSITIONS = \
    [(JobStatus.CREATED, JobStatus.SUBMITTED),
     (JobStatus.SUBMITTED, JobStatus.SUBMIT_FAILED),
     (JobStatus.SUBMITTED, JobStatus.SUCCES),
     (JobStatus.SUBMITTED, JobStatus.FAILED)]
# yapf: enable
