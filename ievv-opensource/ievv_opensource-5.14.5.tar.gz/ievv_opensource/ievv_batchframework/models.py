import json

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class BatchOperationManager(models.Manager):
    """
    Manager for :class:`.BatchOperation`.
    """
    def __create(self, input_data, **kwargs):
        batchoperation = BatchOperation(**kwargs)
        if input_data:
            batchoperation.input_data = input_data
        batchoperation.clean()
        batchoperation.save()
        return batchoperation

    def create_synchronous(self, input_data=None, **kwargs):
        """
        Create a synchronous :class:`.BatchOperation`.

        An synchronous batch operation starts with :obj:`.BatchOperation.status` set
        to :obj:`.BatchOperation.STATUS_RUNNING` and ``started_running_datetime``
        set just as if :meth:`.BatchOperation.mark_as_running` was called. So
        calling this would have the same result as calling :meth:`.create_asynchronous`
        and then calling :meth:`.BatchOperation.mark_as_running`, but this will
        just use one database query instead of two.

        The :class:`.BatchOperation` is cleaned before it is saved.

        Args:
            input_data: The input data.
                A python object to set as the input data using the
                :meth:`.BatchOperation.input_data` property.
            **kwargs: Forwarded to the constructor for :class:`.BatchOperation`.

        Returns:
            BatchOperation: The created BatchOperation object.
        """
        return self.__create(input_data=input_data,
                             status=BatchOperation.STATUS_RUNNING,
                             started_running_datetime=timezone.now(),
                             **kwargs)

    def create_asynchronous(self, input_data=None, **kwargs):
        """
        Create an asynchronous :class:`.BatchOperation`. An asynchronous
        batch operation starts with :obj:`.BatchOperation.status` set
        to :obj:`.BatchOperation.STATUS_UNPROCESSED`.

        The :class:`.BatchOperation` is cleaned before it is saved.

        Args:
            input_data: The input data.
                A python object to set as the input data using the
                :meth:`.BatchOperation.input_data` property.
            **kwargs: Forwarded to the constructor for :class:`.BatchOperation`.

        Returns:
            BatchOperation: The created BatchOperation object.
        """
        return self.__create(input_data=input_data, **kwargs)


class BatchOperation(models.Model):
    """
    Defines a batch operation.
    """

    objects = BatchOperationManager()

    #: One of the possible values for :obj:`~.BatchOperation.status`.
    #: Defines the BatchOperation as uprocessed (not yet started).
    #: This only makes sense for background tasks. They will typically
    #: be created with the unprocessed status, and then set to
    #: :obj:`~.BatchOperation.STATUS_RUNNING` when the batching service
    #: starts running the operation.
    STATUS_UNPROCESSED = 'unprocessed'

    #: One of the possible values for :obj:`~.BatchOperation.status`.
    #: Defines the BatchOperation as running (in progress).
    STATUS_RUNNING = 'running'

    #: One of the possible values for :obj:`~.BatchOperation.status`.
    #: Defines the BatchOperation as finished.
    STATUS_FINISHED = 'finished'

    #: Allowed values for :obj:`~.BatchOperation.status`.
    #: Possible values are:
    #:
    #: - :obj:`~.BatchOperation.STATUS_UNPROCESSED`.
    #: - :obj:`~.BatchOperation.STATUS_RUNNING`.
    #: - :obj:`~.BatchOperation.STATUS_FINISHED`.
    STATUS_CHOICES = [
        (STATUS_UNPROCESSED, 'unprocessed'),
        (STATUS_RUNNING, 'running'),
        (STATUS_FINISHED, 'finished'),
    ]

    #: One of the possible values for :obj:`~.BatchOperation.result`.
    #: This is used when we have no result yet (the operation is not finished).
    RESULT_NOT_AVAILABLE = 'not-available'

    #: One of the possible values for :obj:`~.BatchOperation.result`.
    #: Defines the BatchOperation as failed. This is set if the operation
    #: could not be completed because of an error. Any details about the
    #: result of the operation can be stored in :obj:`~.BatchOperation.output_data_json`.
    RESULT_SUCCESSFUL = 'successful'

    #: One of the possible values for :obj:`~.BatchOperation.result`.
    #: Defines the BatchOperation as failed. This is set if the operation
    #: could not be completed because of an error. Any error message(s)
    #: should be stored in :obj:`~.BatchOperation.output_data_json`.
    RESULT_FAILED = 'failed'

    #: Allowed values for :obj:`~.BatchOperation.result`.
    #: Possible values are:
    #:
    #: - :obj:`~.BatchOperation.RESULT_NOT_AVAILABLE`.
    #: - :obj:`~.BatchOperation.RESULT_SUCCESSFUL`.
    #: - :obj:`~.BatchOperation.RESULT_FAILED`.
    RESULT_CHOICES = [
        (RESULT_NOT_AVAILABLE, 'not available yet (processing not finished)'),
        (RESULT_SUCCESSFUL, 'successful'),
        (RESULT_FAILED, 'failed'),
    ]

    #: The user that started this batch operation.
    #: Optional, but it is good metadata to add for debugging.
    started_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True, blank=True)

    #: The datetime when this batch operation was created.
    #: Defaults to ``timezone.now()``.
    created_datetime = models.DateTimeField(
        default=timezone.now)

    #: The datetime when this batch operation started running.
    #: This is not the same as :obj:`~.BatchOperation.created_datetime`,
    #: this is the time when the operation started processing.
    started_running_datetime = models.DateTimeField(
        null=True, blank=True)

    #: The datetime when this batch operation was finished.
    finished_datetime = models.DateTimeField(
        null=True, blank=True)

    # #: Is this an asynchronous operation? Set this to ``True`` for
    # #: background tasks (such as Celery tasks).
    # asynchronous = models.BooleanField(
    #     default=False)

    #: The content type for :obj:`~.BatchOperation.context_object`.
    context_content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    #: The id field for :obj:`~.BatchOperation.context_object`.
    context_object_id = models.PositiveIntegerField(
        null=True, blank=True)

    #: Generic foreign key that identifies the context this operation
    #: runs in. This is optional.
    context_object = GenericForeignKey('context_content_type', 'context_object_id')

    #: The type of operation. This is application specific - you
    #: typically use this if you allow multiple different batch operations
    #: on the same :obj:`~BatchOperation.context_object`.
    #: This is not required, and defaults to empty string.
    operationtype = models.CharField(
        max_length=255, db_index=True,
        null=False, blank=True, default='')

    #: The status of the operation.
    #: The allowed values for this field is documented in
    #: :obj:`~.BatchOperation.STATUS_CHOICES`.
    #: Defaults to :obj:`~.BatchOperation.STATUS_UNPROCESSED`.
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_UNPROCESSED)

    #: The result of the operation.
    #: The allowed values for this field is documented in
    #: :obj:`~.BatchOperation.RESULT_CHOICES`.
    #: Defaults to :obj:`~.BatchOperation.RESULT_NOT_AVAILABLE`.
    result = models.CharField(
        max_length=13,
        choices=RESULT_CHOICES,
        default=RESULT_NOT_AVAILABLE)

    #: Input data for the BatchOperation.
    #: You should not use this directly, use the :obj:`~.BatchOperation.input_data`
    #: property instead.
    input_data_json = models.TextField(
        null=False, blank=True, default='')

    #: Output data for the BatchOperation.
    #: You should not use this directly, use the :obj:`~.BatchOperation.output_data`
    #: property instead.
    output_data_json = models.TextField(
        null=False, blank=True, default='')

    class Meta:
        ordering = ['-created_datetime']

    @property
    def input_data(self):
        """
        Decode :obj:`.BatchOperation.input_data_json` and return the result.

        Return `None` if input_data_json is empty.
        """
        if self.input_data_json:
            if not hasattr(self, '_input_data'):
                # Store the decoded input_data to avoid re-decoding the json for
                # each access. We invalidate this cache in the setter.
                self._input_data = json.loads(self.input_data_json)
            return self._input_data
        else:
            return None

    @input_data.setter
    def input_data(self, input_data):
        """
        Set :obj:`.BatchOperation.input_data_json`. Encodes the given
        input_data using `json.dumps`.
        """
        self.input_data_json = json.dumps(input_data)
        if hasattr(self, '_input_data'):
            delattr(self, '_input_data')

    @property
    def output_data(self):
        """
        Decode :obj:`.BatchOperation.output_data_json` and return the result.

        Returns:
            object: `None` if output_data_json is empty, or the decoded json data
            if the ``output_data`` is not empty.
        """
        if self.output_data_json:
            if not hasattr(self, '_output_data'):
                # Store the decoded output_data to avoid re-decoding the json for
                # each access. We invalidate this cache in the setter.
                self._output_data = json.loads(self.output_data_json)
            return self._output_data
        else:
            return None

    @output_data.setter
    def output_data(self, output_data):
        """
        Set :obj:`.BatchOperation.output_data_json`. Encodes the given
        output_data using `json.dumps`.

        Returns:
            object: `None` if output_data_json is empty, or the decoded json data
            if the ``output_data`` is not empty.
        """
        self.output_data_json = json.dumps(output_data)
        if hasattr(self, '_output_data'):
            delattr(self, '_output_data')

    def mark_as_running(self):
        """
        Mark the batch operation as running.

        Sets the :obj:`.status` to :obj:`.STATUS_RUNNING`,
        :obj:`.started_running_datetime` to the current datetime,
        clean and save.
        """
        self.status = self.STATUS_RUNNING
        self.started_running_datetime = timezone.now()
        self.clean()
        self.save()

    def finish(self, failed=False, output_data=None):
        """
        Mark the bulk operation as finished.

        Sets :obj:`.result` as documented in the ``failed`` parameter below.
        Sets :obj:`.finished_datetime` to the current datetime.
        Sets :obj:`.output_data_json` as documented in the ``output_data``
        parameter below.

        Args:
            failed (boolean): Set this to ``False`` to set :obj:`.result` to
                :obj:`.RESULT_FAILED`. The default is ``True``, which means that
                :obj:`.result` is set to :obj:`.RESULT_SUCCESSFUL`
            output_data: The output data.
                A python object to set as the output data using the
                :meth:`.BatchOperation.output_data` property.
        """
        if failed:
            self.result = self.RESULT_FAILED
        else:
            self.result = self.RESULT_SUCCESSFUL
        if output_data:
            self.output_data = output_data
        self.status = self.STATUS_FINISHED
        self.finished_datetime = timezone.now()
        self.clean()
        self.save()

    def clean(self):
        if self.status == self.STATUS_FINISHED and self.result == self.RESULT_NOT_AVAILABLE:
            raise ValidationError({
                'result': 'Must be "successful" or "failed" when status is "finished".'
            })
        if self.status != self.STATUS_UNPROCESSED and self.started_running_datetime is None:
            raise ValidationError({
                'started_running_datetime': 'Can not be None when status is "running" or "finished".'
            })

    def __str__(self):
        return \
            '#{id}-{operationtype}({created_datetime})[{status}, {result}]' \
            ' - {context_content_type}#{context_object_id}'.format(
                id=self.id,
                operationtype=self.operationtype,
                created_datetime=self.created_datetime,
                status=self.status,
                result=self.result,
                context_content_type=self.context_content_type,
                context_object_id=self.context_object_id
            )
