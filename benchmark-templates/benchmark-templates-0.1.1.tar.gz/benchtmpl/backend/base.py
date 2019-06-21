# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Abstract interface for the workflow execution engine. The reproducible
benchmark engine is flexible with respect to the workflow engine that is being
used.

Each engine has to implement the abstract workflow engine class that is defined
in this module. The engine is responsible for interpreting a given workflow
template and a set of template parameter arguments. The engine is also
responsible for retrieving output files and for providing access to these files.
"""

from abc import abstractmethod


class WorkflowEngine(object):
    """The workflow engine is used to execute workflow templates for a given
    set of arguments for template parameters as well as to check the state of
    the workflow execution.

    Workflow executions, referred to as runs, are identified by unique run ids
    that are assigned by the engine when the execution starts.
    """
    @abstractmethod
    def cancel_run(self, run_id):
        """Request to cancel execution of the given run.

        Parameters
        ----------
        run_id: string
            Unique run identifier
        """
        raise NotImplementedError()

    @abstractmethod
    def exec(self, template, arguments):
        """Execute a given workflow template for a set of argument values.
        Returns an unique identifier for the started workflow run.

        Parameters
        ----------
        template: benchtmpl.workflow.template.base.TemplateHandle
            Workflow template containing the parameterized specification and the
            parameter declarations
        arguments: dict(benchtmpl.workflow.parameter.value.TemplateArgument)
            Dictionary of argument values for parameters in the template

        Returns
        -------
        string
        """
        raise NotImplementedError()

    @abstractmethod
    def get_state(self, run_id):
        """Get the status of the workflow with the given identifier.

        Parameters
        ----------
        run_id: string
            Unique run identifier

        Returns
        -------
        benchtmpl.workflow.state.WorkflowState

        Raises
        ------
        benchtmpl.error.UnknownRunError
        """
        raise NotImplementedError()
