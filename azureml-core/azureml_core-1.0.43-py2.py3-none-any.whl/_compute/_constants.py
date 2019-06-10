# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

MLC_WORKSPACE_API_VERSION = '2018-11-19'
MLC_COMPUTE_RESOURCE_ID_FMT = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/' \
                              'workspaces/{}/computes/{}'
MLC_ENDPOINT_FMT = 'https://management.azure.com{}'.format(MLC_COMPUTE_RESOURCE_ID_FMT)
