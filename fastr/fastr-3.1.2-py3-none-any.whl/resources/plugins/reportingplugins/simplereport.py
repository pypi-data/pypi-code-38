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

import os

from fastr import version
from fastr.helpers import log
from fastr.execution.networkrun import NetworkRun
from fastr.plugins.reportingplugin import ReportingPlugin


class SimpleReport(ReportingPlugin):
    def run_finished(self, run: NetworkRun):
        log.info('===== RESULTS =====')
        result = True
        for sink_node, sink_data in sorted(run.sink_results.items()):
            nr_failed = sum(len(x[1]) > 0 for x in sink_data.values())
            nr_success = len(sink_data) - nr_failed

            if nr_failed > 0:
                result = False

            log.info('{}: {} success / {} failed'.format(sink_node, nr_success, nr_failed))
        log.info('===================')

        if not result:
            sink_result_file = os.path.join(run.tmpdir, run.SINK_DUMP_FILE_NAME)

            log.warning(
                """There were failed samples in the run, to start debugging you can run:

    fastr trace {sink_data_file} --sinks

see the debug section in the manual at https://fastr.readthedocs.io/en/{branch}/static/user_manual.html#debugging for more information.""".format(
                    sink_data_file=sink_result_file,
                    branch='default' if version.hg_branch == 'default' else 'develop',
                )
            )
