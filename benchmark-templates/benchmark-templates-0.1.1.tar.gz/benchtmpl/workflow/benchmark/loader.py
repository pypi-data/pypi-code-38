# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Implementation of the template loader for benchmark workflow templates. A
benchmark template has one additional element in its serialization that contains
the specification of the result schema.
"""

from benchtmpl.workflow.benchmark.base import BenchmarkTemplate
from benchtmpl.workflow.benchmark.schema import BenchmarkResultSchema
from benchtmpl.workflow.template.loader import DefaultTemplateLoader

import benchtmpl.error as err


"""Additional top-level elements of dictionary serialization for benchmark
template handles.
"""
LABEL_RESULTS = 'results'


class BenchmarkTemplateLoader(DefaultTemplateLoader):
    """Implementation of the template loader for benchmark workflow templates.
    """
    def from_dict(self, doc, identifier=None, base_dir=None, validate=True):
        """Create an instance of the benchmark template from a dictionary
        serialization. Expects a dictionary that contains the three top-level
        elements of the template handle plus the 'result' schema.

        Parameters
        ----------
        dict: dict
            Dictionary serialization of a workflow template
        identifier: string, optional
            Unique template identifier. This value will override the value in
            the document.
        base_dir: string, optional
            Optional path to directory on disk that contains static files that
            are required to run the represented workflow. This value will
            override the value in the document.
        validate: bool, optional
            Flag indicating if given template parameter declarations are to be
            validated against the parameter schema or not.

        Returns
        -------
        benchtmpl.workflow.benchmark.base.BenchmarkTemplate

        Raises
        ------
        benchtmpl.error.InvalidTemplateError
        benchtmpl.error.UnknownParameterError
        """
        # Ensure that the mandatory elements are present
        if not LABEL_RESULTS in doc:
            raise err.InvalidTemplateError('missing element \'{}\''.format(LABEL_RESULTS))
        # Get handle for workflow template from super class
        template = super(BenchmarkTemplateLoader, self).from_dict(
            doc=doc,
            identifier=identifier,
            base_dir=base_dir,
            validate=validate
        )
        # Get schema object from serialization
        try:
            schema = BenchmarkResultSchema.from_dict(doc[LABEL_RESULTS])
        except ValueError as ex:
            raise err.InvalidTemplateError(str(ex))
        return BenchmarkTemplate(
            identifier=template.identifier,
            base_dir=template.base_dir,
            workflow_spec=template.workflow_spec,
            parameters=template.parameters.values(),
            schema=schema
        )

    def to_dict(self, template):
        """Get dictionary serializationfor the wrokflow template.

        Parameters
        ----------
        template: benchtmpl.workflow.benchmark.base.BenchmarkTemplate
            Expects an instance of a benchmark template handle

        Returns
        -------
        dict
        """
        # Add serialization of schema to the serialization of the super class
        obj = super(BenchmarkTemplateLoader, self).to_dict(template)
        obj[LABEL_RESULTS] = template.schema.to_dict()
        return obj
