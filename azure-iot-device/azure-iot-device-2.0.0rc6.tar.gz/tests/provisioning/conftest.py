# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import pytest

collect_ignore = []

# Ignore Async tests if below Python 3.5
if sys.version_info < (3, 5):
    collect_ignore.append("aio")
