# 
# Copyright 2014, 2019 by Delphix
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
from contextlib import contextmanager
from delphixpy.v1_6_2 import exceptions

VERBOSE_ENGINES = set()


def set_verbose(engine, verbose=True):
    if verbose:
        VERBOSE_ENGINES.add(engine.address)
    else:
        VERBOSE_ENGINES.remove(engine.address)


class JobMode(object):
    ASYNC = 'ASYNC'
    SYNC = 'SYNC'


@contextmanager
def async(engine):
    try:
        engine.job_contexts.append((JobMode.ASYNC, []))
        yield
    finally:
        jobs = engine.job_contexts.pop()[1]
        for job_ref in jobs:
            wait(engine, job_ref)


@contextmanager
def sync(engine):
    try:
        engine.job_contexts.append((JobMode.SYNC, None))
        yield
    finally:
        engine.job_contexts.pop()


def wait(engine, job_ref):
    from delphixpy.v1_6_2.web import job
    status = None
    event_counter = 0
    while True:
        job_obj = job.get(engine, job_ref)
        if engine.address in VERBOSE_ENGINES:
            if job_obj.events[event_counter:]:
                for evt in job_obj.events[event_counter:]:
                    print(evt.message_details)
                event_counter += len(job_obj.events[event_counter:])
        status = job_obj.parent_action_state
        if status in ['EXECUTING', 'WAITING']:
            time.sleep(1)
            continue
        elif status == 'COMPLETED':
            break
        else:
            msg = "Job '%s' failed." % job_ref
            raise exceptions.JobError(msg, job_obj)