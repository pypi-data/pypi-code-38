# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holding the execution context class."""


class ExecutionContext(object):
    """
    Class containing the information needed for ClientRunner execution context.

    This class object is passed to subprocess, so it should be serializable.
    """

    def __init__(self, run_id: str):
        """
        Construct ExecutionContext object.

        :param run_id: client run id
        """
        self.run_id = run_id
