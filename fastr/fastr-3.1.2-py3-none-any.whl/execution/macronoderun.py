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

from fastr.core import vfs_plugin
from fastr.core.dimension import Dimension
from fastr.core.samples import SampleItem
from .inputoutputrun import MacroOutputRun
from .job import SinkJob, Job, JobState
from .networkrun import NetworkRun
from .noderun import NodeRun
from fastr.helpers import log

__all__ = ['MacroNodeRun']


class MacroNodeRun(NodeRun):
    """
    MacroNodeRun encapsulates an entire network in a single node.
    """
    _OutputType = MacroOutputRun

    def __init__(self, node, parent):
        """
        :param network: network to create macronode for
        :type network: fastr.planning.network.Network
        """
        super(MacroNodeRun, self).__init__(node=node, parent=parent)

        self._network_run = NetworkRun(node.network)
        self.network_run.parent = self

    @property
    def network_run(self):
        return self._network_run

    def __getstate__(self):
        """
        Retrieve the state of the MacroNodeRun

        :return: the state of the object
        :rtype dict:
        """
        state = super(MacroNodeRun, self).__getstate__()
        state['network_run'] = self._network_run.__getstate__()
        return state

    def __setstate__(self, state):
        self._network_run = NetworkRun.createobj(state.pop('network_run'))
        super(MacroNodeRun, self).__setstate__(state)

    def get_output_info(self, output):
        source_dimensions = {}

        for input_ in self.inputs.values():
            source_node = self.network_run.sourcelist[input_.id]
            source_dimension_name = source_node.dimnames[0]
            source_dimensions[source_dimension_name] = input_.dimensions

        # Translate back result index and id
        sink = self.network_run.sinklist[output.id]
        new_dimensions = []

        for dimname, size in zip(sink.dimnames, sink.outputsize):
            # If they were translated, replace them back
            if dimname in source_dimensions:
                dimensions_part = source_dimensions[dimname]

                new_dimensions.extend(x.copy() for x in dimensions_part)
            else:
                new_dimensions = Dimension(dimname, size)

        return tuple(new_dimensions)

    def execute(self):
        # Should we check validity of the node and inside network again?
        # Prepare the output of the Node
        source_data = {}
        sink_data = {}
        network_run = self.network_run

        # The data required to map the linearized samples back to original format
        source_dimensions = {}

        # Set environment for network
        network_run.executing = True
        network_run.tmpdir = os.path.join(self.parent.tmpdir, self.id)
        network_run.tmpurl = vfs_plugin.path_to_url(network_run.tmpdir)
        network_run.timestamp = self.parent.timestamp

        for input_ in self.inputs.values():
            source_node = network_run.sourcelist[input_.id]

            # Register dimension name for source
            sample_mapping = {}

            if source_node.dimnames[0] not in source_dimensions:
                source_dimensions[source_node.dimnames[0]] = sample_mapping

            for index, sample_item in enumerate(input_.items()):
                sample_mapping[index] = sample_item.index, sample_item.id

                new_sample = SampleItem(
                    index,
                    '+'.join(sample_item.id),
                    sample_item.data,
                    sample_item.jobs,
                    sample_item.failed_annotations,
                )

                source_node.output[new_sample] = new_sample

                dummy_job = Job(source_node,
                                sample_item.id,
                                sample_item.index,
                                [],
                                [])
                dummy_job.status = JobState.finished

            # Data is put straight in the output, add empty dummy
            source_data[input_.id] = []

        for output in self.outputs.values():
            # Set datatype for sink to match requested datatype on output
            self.network_run.sinklist[output.id].datatype = output.resulting_datatype

            # Set sink data to ignore
            sink_data[output.id] = 'null://ignore/sinks'

        # Set the data for the network
        network_run.set_data(source_data, sink_data)

        # Start generating jobs
        for job_list in network_run.generate_jobs():
            # Stop if execution ended
            if not self.parent.executing:
                network_run.executing = self.parent.executing
                return

            yield [x for x in job_list if not isinstance(x, SinkJob)]

        for sink in network_run.sinklist.values():
            sink.update()  # Make sure the sink is updated
            log.debug('Getting results from sink {} with dimnames: {}'.format(sink.global_id, sink.dimnames))
            output = self.outputs[sink.id]

            # Copy sink data to node
            for sample_item in sink.input.items():

                new_id = []
                new_index = []

                # Translate back result index and id
                for dimname, index_part, id_part in zip(sink.dimnames, sample_item.index, sample_item.id):
                    # If they were translated, replace them back
                    if dimname in source_dimensions:
                        index_part, id_part = source_dimensions[dimname][index_part]
                        new_index.extend(index_part)
                        new_id.extend(id_part)
                    else:
                        new_index.append(index_part)
                        new_id.append(id_part)

                new_sample = SampleItem(
                    new_index,
                    new_id,
                    sample_item.data,
                    sample_item.jobs,
                    sample_item.failed_annotations,
                )

                log.debug("Setting {} in {}".format(new_sample, output.fullid))
                output[new_sample] = new_sample

                dummy_job = Job(sink,
                                sample_item.id,
                                sample_item.index,
                                [],
                                [])
                dummy_job.status = JobState.finished

        # Only now the NodeRun is drained of all jobs
        self.drained = True
