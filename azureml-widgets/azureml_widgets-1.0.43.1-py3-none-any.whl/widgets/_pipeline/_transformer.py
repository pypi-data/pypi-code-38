# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.widgets._transformer import _DataTransformer
from azureml.pipeline.core import StepRun


class _PipelineGraphTransformer(_DataTransformer):

    def _transform_graph(self, graph, child_runs):
        transform_graph = {
            'datasource_nodes': {},
            'module_nodes': {},
            'edges': [],
            'child_runs': {}
        }

        if graph:
            for node in graph.datasource_nodes:
                transform_graph['datasource_nodes'][node.node_id] = {
                    'node_id': node.node_id,
                    'name': node.name
                }

            for node in graph.module_nodes:
                transform_graph['module_nodes'][node.node_id] = {
                    'node_id': node.node_id,
                    'name': node.name,
                    'status': 'NotStarted',
                }
                transform_graph['child_runs'][node.node_id] = {
                    'run_id': '',
                    'name': node.name,
                    'status': 'NotStarted',
                    'start_time': '',
                    'created_time': '',
                    'end_time': '',
                    'duration': ''
                }

            for node in graph.module_nodes:
                for node_input in node.inputs:
                    if node_input.incoming_edge is not None:
                        source_node = node_input.incoming_edge.source_port.node
                        transform_graph['edges'].append({
                            'source_node_id': source_node.node_id,
                            'source_node_name': source_node.name,
                            'source_name': ''.join(list(source_node.output_dict.keys())[0]),
                            'target_name': ''.join(list(node.input_dict.keys())[0]),
                            'dst_node_id': node.node_id,
                            'dst_node_name': node.name
                        })

            for child_run in child_runs:
                if not isinstance(child_run, StepRun):
                    continue

                node_id = child_run._node_id
                transform_graph['module_nodes'][node_id]['_is_reused'] = child_run._is_reused

                node = graph.get_node(node_id)

                transform_graph['module_nodes'][node_id]['status'] = child_run.get_status()
                transform_graph['module_nodes'][node_id]['run_id'] = child_run.id
                transform_run = self._transform_run(child_run)
                transform_run['name'] = node.name
                transform_run['is_reused'] = "Yes" if child_run._is_reused else ""
                transform_graph['child_runs'][node_id] = {**transform_graph['child_runs'][node_id], **transform_run}
                transform_graph['child_runs'][node_id]['status'] = child_run.get_status()

            transform_graph['child_runs'] = list(transform_graph['child_runs'].values())
        return transform_graph
