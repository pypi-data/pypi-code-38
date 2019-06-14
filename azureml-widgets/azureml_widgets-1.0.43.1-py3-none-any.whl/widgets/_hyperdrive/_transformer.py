# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re

from azureml.widgets._transformer import _DataTransformer


class _HyperDriveDataTransformer(_DataTransformer):
    """Transform run and metric data for HyperDrive runs."""

    def _get_additional_properties(self, run):
        property_bag = run._run_dto['properties']
        arguments = property_bag['Arguments'] if 'Arguments' in property_bag else None
        hyperdrive_job_id = self._get_hyperdrive_run_id(run.id)

        return {
            'hyperdrive_id': hyperdrive_job_id,
            'arguments': arguments
        }

    @staticmethod
    def _get_hyperdrive_run_id(run_id):
        found_group = re.search(r'([^_]*)_[^_]*$', run_id)
        if found_group is not None:
            return found_group.group(1)
        return run_id
