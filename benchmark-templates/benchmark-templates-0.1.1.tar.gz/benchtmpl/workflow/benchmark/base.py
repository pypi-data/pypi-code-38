# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Extended workflow template for data analytics benchmarks. The benchmark
template extends the base template with one element that contains the
specification for the benchmark result.

The assumption is that the workflow for the benchmark contains one step that
generates a result file. This file is expected to contain a JSON or YAML object
with the summarized results for the benchmark workflow run. These results are
used to generate the overall benchmark leaderboard.

The structure of the benchmark result element is defined in the schema module.
"""

from benchtmpl.workflow.template.base import TemplateHandle


class BenchmarkTemplate(TemplateHandle):
    """Extended workflow template for data analytics benchmarks that add the
    result schema object to the base template.
    """
    def __init__(self, workflow_spec, schema, identifier=None, base_dir=None, parameters=None):
        """Initialize the components of the benchmark template. A super class
        raises an error if the identifier of template parameters are not unique.

        Parameters
        ----------
        workflow_spec: dict
            Workflow specification object
        schema: benchtmpl.workflow.benachmark.schema.BenchmarkResultSchema
            Schema of the result file that is generated for each workflow run
        identifier: string, optional
            Unique template identifier. If no value is given a UUID will be
            assigned.
        base_dir: string, optional
            Optional path to directory on disk that contains static files that
            are required to run the represented workflow
        parameters: list(benchtmpl.workflow.parameter.base.TemplateParameter), optional
            List of workflow template parameter declarations

        Raises
        ------
        benchtmpl.error.InvalidTemplateError
        """
        super(BenchmarkTemplate, self).__init__(
            workflow_spec=workflow_spec,
            identifier=identifier,
            base_dir=base_dir,
            parameters=parameters
        )
        self.schema = schema
