from __future__ import absolute_import

import django_rq

from ievv_opensource.ievv_batchframework.models import BatchOperation
from ievv_opensource.ievv_batchframework import batchregistry

import logging


class BatchActionGroupTask(object):
    abstract = True

    def run_actiongroup(self, actiongroup_name, batchoperation_id, **kwargs):
        try:
            batchoperation = BatchOperation.objects\
                .get(id=batchoperation_id, status=BatchOperation.STATUS_UNPROCESSED)
        except BatchOperation.DoesNotExist:
            logging.warning('BatchOperation with id={} does not exist, or is already running.')
            return
        else:
            batchoperation.mark_as_running()
            registry = batchregistry.Registry.get_instance()
            full_kwargs = {
                'started_by': batchoperation.started_by,
                'context_object': batchoperation.context_object,
            }
            full_kwargs.update(kwargs)
            actiongroupresult = registry.get_actiongroup(actiongroup_name)\
                .run_blocking(**full_kwargs)
            batchoperation.finish(failed=actiongroupresult.failed,
                                  output_data=actiongroupresult.to_dict())


@django_rq.job('default')
def default(**kwargs):
    BatchActionGroupTask().run_actiongroup(**kwargs)


@django_rq.job('highpriority')
def highpriority(**kwargs):
    BatchActionGroupTask().run_actiongroup(**kwargs)
