# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
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

from logging import LogRecord

from fastr.abc.baseplugin import Plugin
from fastr.execution.job import Job
from fastr.execution.networkrun import NetworkRun
from fastr.helpers.events import EventType, register_listener, remove_listener


class ReportingPlugin(Plugin):
    """
    Base class for all reporting plugins. The plugin has a number of methods that
    can be implemented that will be called on certain events. On these events the
    plugin can inspect the presented data and take reporting actions.
    """
    _instantiate = True

    def activate(self):
        if self.job_updated.__qualname__ != 'ReportingPlugin.job_updated':
            register_listener(EventType.job_updated, self.job_updated)

        if self.run_started.__qualname__ != 'ReportingPlugin.run_started':
            register_listener(EventType.run_started, self.run_started)

        if self.run_finished.__qualname__ != 'ReportingPlugin.run_finished':
            register_listener(EventType.run_finished, self.run_finished)

        if self.log_record_emitted.__qualname__ != 'ReportingPlugin.log_record_emitted':
            register_listener(EventType.log_record_emitted, self.log_record_emitted)

    def deactivate(self):
        remove_listener(EventType.job_updated, self.job_updated)
        remove_listener(EventType.run_started, self.run_started)
        remove_listener(EventType.run_finished, self.run_finished)
        remove_listener(EventType.log_record_emitted, self.log_record_emitted)

    def job_updated(self, job: Job):
        pass

    def run_started(self, run: NetworkRun):
        pass

    def run_finished(self, run: NetworkRun):
        pass

    def log_record_emitted(self, record: LogRecord):
        pass


