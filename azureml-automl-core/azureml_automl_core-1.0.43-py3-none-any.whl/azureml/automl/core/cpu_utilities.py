# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility for getting CPU related information during AutoML training."""
from typing import Optional


def _get_num_physical_cpu_cores_model_explanations(max_cores_per_iteration: Optional[int] = None) -> int:
    """Return the number of CPU cores for explainable model for model explanations."""
    if max_cores_per_iteration is not None:
        return max_cores_per_iteration

    num_cpu_core = None
    try:
        import psutil
        num_cpu_core = psutil.cpu_count(logical=False)
    except Exception:
        # LightGBM doesn't perform as well if the number of jobs are set to available number
        # of logical cores. So approximating the number of cores to half of what is available.
        import os
        num_cpu_core = os.cpu_count()
        if num_cpu_core is not None:
            num_cpu_core /= 2

    if num_cpu_core is None:
        # Default to one cpu core if platform APIs don't return any value
        return 1
    else:
        return int(num_cpu_core)
