# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import voluptuous as v
from zuul.trigger import BaseTrigger
from zuul.driver.pagure.paguremodel import PagureEventFilter
from zuul.driver.util import scalar_or_list, to_list


class PagureTrigger(BaseTrigger):
    name = 'pagure'
    log = logging.getLogger("zuul.trigger.PagureTrigger")

    def getEventFilters(self, trigger_config):
        efilters = []
        for trigger in to_list(trigger_config):
            f = PagureEventFilter(
                trigger=self,
                types=to_list(trigger['event']),
                actions=to_list(trigger.get('action')),
                refs=to_list(trigger.get('ref')),
                comments=to_list(trigger.get('comment')),
                statuses=to_list(trigger.get('status')),
            )
            efilters.append(f)

        return efilters

    def onPullRequest(self, payload):
        pass


def getSchema():
    pagure_trigger = {
        v.Required('event'):
            # Cannot use same event type than github as it collapse
            # with Registered github triggers if any. The Event filter
            # does not have the connections info like the Ref filter (require)
            # have. See manager/__init__.py:addChange
            scalar_or_list(v.Any('pg_pull_request',
                                 'pg_pull_request_review',
                                 'pg_push')),
        'action': scalar_or_list(str),
        'ref': scalar_or_list(str),
        'comment': scalar_or_list(str),
        'status': scalar_or_list(str),
    }

    return pagure_trigger
