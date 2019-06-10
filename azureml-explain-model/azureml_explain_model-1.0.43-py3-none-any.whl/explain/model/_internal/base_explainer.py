# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the base explainer to explain and visualize the feature importances of a model."""

import os
import json
import io
from math import ceil

try:
    from azureml._restclient.constants import RUN_ORIGIN
    from azureml.core import Experiment, Run
except ImportError:
    print("Could not import azureml.core, required if using run history")
from .common import module_logger
from .constants import History


class BaseExplainer:
    """The base class for explainers."""
    def __init__(self, workspace=None, experiment_name=None, run_id=None):
        """Initializes the explainer.

        :param workspace: An object that represents a workspace.
        :type workspace: azureml.core.workspace.Workspace
        :param experiment_name: The name of an experiment.
        :type experiment_name: str
        :param run_id: A GUID that represents a run.
        :type run_id: str
        """
        self.run = None
        self.storage_policy = {History.MAX_NUM_BLOCKS: 3, History.BLOCK_SIZE: 100}
        args_none = [arg is None for arg in [workspace, experiment_name]]
        # Validate either all the arguments above are specified or all are None
        if not any(args_none):
            experiment = Experiment(workspace, experiment_name)
            if run_id is None:
                # Create a new run
                self.run = experiment.start_logging(snapshot_directory=None)
            else:
                # Create a run object to reference the original one with the same run_id
                self.run = Run(experiment, run_id=run_id)
        elif not all(args_none):
            raise ValueError('Both or neither of workspace and experiment name need to be specified')

    def _order_imp(self, summary):
        return summary.argsort()[..., ::-1]

    def _create_upload_dir(self):
        # create the outputs folder
        upload_dir = './explanation/'
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def _upload_artifact(self, upload_dir, artifact_name, values):
        try:
            json_string = json.dumps(values)
            stream = io.BytesIO(json_string.encode('utf-8'))
            self.run.upload_file('{}{}.json'.format(upload_dir.lstrip('./'), artifact_name), stream)
        except ValueError as exp:
            module_logger.error('Cannot serialize numpy arrays as JSON')

    def _get_num_of_blocks(self, num_of_columns):
        block_size = self.storage_policy[History.BLOCK_SIZE]
        num_blocks = ceil(num_of_columns / block_size)
        max_num_blocks = self.storage_policy[History.MAX_NUM_BLOCKS]
        if num_blocks > max_num_blocks:
            num_blocks = max_num_blocks
        return num_blocks

    def _get_model_summary_artifacts(self, upload_dir, name, summary):
        module_logger.debug('Uploading model summary')
        num_columns = summary.shape[len(summary.shape) - 1]
        num_blocks = self._get_num_of_blocks(num_columns)
        block_size = self.storage_policy[History.BLOCK_SIZE]
        storage_metadata = {
            History.NAME: name,
            History.MAX_NUM_BLOCKS: self.storage_policy[History.MAX_NUM_BLOCKS],
            History.BLOCK_SIZE: self.storage_policy[History.BLOCK_SIZE],
            History.NUM_FEATURES: num_columns,
            History.NUM_BLOCKS: num_blocks
        }
        artifacts = [{} for _ in range(num_blocks)]
        # Chunk the summary and save it to Artifact
        start = 0
        for idx in range(num_blocks):
            if idx == num_blocks - 1:
                # on last iteration, grab everything that's left for the last block
                cols = slice(start, num_columns)
            else:
                cols = slice(start, start + block_size)
            block = summary[..., cols]
            block_name = '{}_{}'.format(name, str(idx))
            module_logger.debug('Uploading artifact for block: {}'.format(block_name))
            self._upload_artifact(upload_dir, block_name, block.tolist())
            artifacts[idx][History.PREFIX] = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                                   self.run.id,
                                                                                   upload_dir,
                                                                                   block_name))
            start += block_size
        return artifacts, storage_metadata

    def get_storage_policy(self):
        """Returns the current storage policy.

        :rtype: dict
        :return: The storage policy represented as a dictionary of settings.
        """
        # return the current storage policy
        return self.storage_policy

    def set_storage_policy(self, block_size=None, max_num_blocks=None):
        """Sets the current storage policy.

        :param block_size: The size of each block for the summary stored in artifacts storage.
        :type block_size: int
        :param max_num_blocks: The maximum number of blocks to store.
        :type max_num_blocks: int
        """
        if block_size is not None:
            self.storage_policy[History.BLOCK_SIZE] = block_size
        if max_num_blocks is not None:
            self.storage_policy[History.MAX_NUM_BLOCKS] = max_num_blocks
