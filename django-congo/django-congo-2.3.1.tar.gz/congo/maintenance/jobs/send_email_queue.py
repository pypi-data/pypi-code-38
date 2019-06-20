# -*- coding: utf-8 -*-
from congo.communication import get_email_message_queue_model
from congo.maintenance.jobs import BaseJob
from collections import OrderedDict
import logging

class Job(BaseJob):
    description = "Sending an e-mail message queue"

    def __init__(self):
        super(Job, self).__init__()

    def _run(self, user, *args, **kwargs):
        result = OrderedDict()

        model = get_email_message_queue_model()
        i, j, k = model.send_messages(user = user)
        result['sent'] = i
        result['package'] = j
        result['total'] = k
        result['level'] = logging.INFO if k else logging.DEBUG

        return result
