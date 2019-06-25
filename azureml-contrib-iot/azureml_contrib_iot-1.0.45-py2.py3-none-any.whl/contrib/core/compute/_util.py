# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from pkg_resources import resource_string

iothub_compute_template = json.loads(
    resource_string(__name__, 'data/iothub_compute_template.json')
    .decode('ascii'))
