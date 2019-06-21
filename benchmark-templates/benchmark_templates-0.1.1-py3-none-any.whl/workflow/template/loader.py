# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The template loader reads and writes template handles from and to files
on disk. This class implements a factory pattern for different variations of
workflow templates. Each variation of the template handle should provide an
implementation of the template loader. Thie loader is used by the template
repository to store and retrieve template specifications.

An implementation for the default base template handle is provided in this
module.
"""

from abc import abstractmethod

from benchtmpl.workflow.parameter.base import TemplateParameter

import benchtmpl.error as err
import benchtmpl.util.core as util
import benchtmpl.workflow.parameter.declaration as pd
import benchtmpl.workflow.parameter.util as putil
import benchtmpl.workflow.template.base as tmpl


"""Top-level elements of dictionary serialization for template handles."""
LABEL_ID = 'id'
LABEL_PARAMETERS = 'parameters'
LABEL_WORKFLOW = 'workflow'


class TemplateLoader(object):
    """The template loader is used by the template repository to store and
    retrieve workflow template specifications on disk.
    """
    @abstractmethod
    def from_dict(self, doc, identifier=None, base_dir=None, validate=True):
        """Create an instance of the template handle for a dictionary
        serialization. The elements in the dictionary and their structure is
        expected to the elements and structure that is produced by the to_dict()
        method.

        An InvalidTemplateError is raised if the dictionary does not represent
        a valid serialization of a workflow handle.

        If the valid flag is True all given template parameter declarations are
        validated against the parameter schema. An InvalidTemplateError is
        raised if (i) any of the given parameter declarations fails the
        validation, or (ii) the workflow specifiction references parameters for
        which no declaration is given.

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
        benchtmpl.workflow.template.base.TemplateHandle

        Raises
        ------
        benchtmpl.error.InvalidTemplateError
        benchtmpl.error.UnknownParameterError
        """
        raise NotImplementedError()

    def load(self, filename, identifier=None, base_dir=None, format=None, validate=True):
        """Create an instance of the template handle for a serialization if the
        template handle that is stored in a file.

        Parameters
        ----------
        filename: string
            Path to a file on disk
        identifier: string, optional
            Unique template identifier. This value will override the value in
            the document.
        base_dir: string, optional
            Optional path to directory on disk that contains static files that
            are required to run the represented workflow. This value will
            override the value in the document.
        format: string, optional
            Optional file format identifier. The default is YAML
        validate: bool, optional
            Flag indicating if given template parameter declarations are to be
            validated against the parameter schema or not.

        Returns
        -------
        benchtmpl.workflow.template.base.TemplateHandle

        Raises
        ------
        benchtmpl.error.InvalidTemplateError
        """
        doc = util.read_object(filename, format=format)
        return self.from_dict(
            doc,
            identifier=identifier,
            base_dir=base_dir,
            validate=validate
        )

    @abstractmethod
    def to_dict(self, template):
        """Get a dictionary serialization for the workflow template.

        Parameters
        ----------
        template: benchtmpl.workflow.template.base.TemplateHandle
            Instance of a template handle class that is supported by the
            template loader

        Returns
        -------
        dict
        """
        raise NotImplementedError()

    def write(self, template, filename, format=None):
        """Write the given template handle to disk.

        Parameters
        ----------
        template: benchtmpl.workflow.template.base.TemplateHandle
            Instance of a template handle class that is supported by the
            template loader
        filename: string
            Path to a file to which the serialized handle is written
        format: string, optional
            Optional file format identifier. The default is YAML

        """
        util.write_object(
            obj=self.to_dict(template),
            filename=filename
        )


class DefaultTemplateLoader(TemplateLoader):
    """Default implementation of the loader class for the basic template handle.
    This is the default loader that is used by the template repository.
    """
    def from_dict(self, doc, identifier=None, base_dir=None, validate=True):
        """Create an instance of the template handle for a dictionary
        serialization. The expected three top-level elements of the dictionary
        are 'workflow', 'id', and 'parameters'. The last two elements are
        optional.

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
        benchtmpl.workflow.template.base.TemplateHandle

        Raises
        ------
        benchtmpl.error.InvalidTemplateError
        benchtmpl.error.UnknownParameterError
        """
        # Ensure that the mandatory elements are present
        if not LABEL_WORKFLOW in doc:
            raise err.InvalidTemplateError('missing element \'{}\''.format(LABEL_WORKFLOW))
        workflow_spec = doc[LABEL_WORKFLOW]
        # Add given parameter declarations to the parameter list. Ensure that
        # all default values are set
        parameters = dict()
        if LABEL_PARAMETERS in doc:
            parameters = putil.create_parameter_index(
                doc[LABEL_PARAMETERS],
                validate=validate
            )
        # Ensure that the workflow specification does not reference undefined
        # parameters if validate flag is True.
        if validate:
            for key in tmpl.get_parameter_references(workflow_spec):
                if not key in parameters:
                    raise err.UnknownParameterError(key)
        # Get identifier if present in document
        if LABEL_ID in doc:
            identifier = doc[LABEL_ID]
        return tmpl.TemplateHandle(
            identifier=identifier,
            base_dir=base_dir,
            workflow_spec=workflow_spec,
            parameters=list(parameters.values())
        )

    def to_dict(self, template):
        """Get dictionary serializationfor the wrokflow template.

        Parameters
        ----------
        template: benchtmpl.workflow.template.base.TemplateHandle
            Instance of a template handle class that is supported by the
            template loader

        Returns
        -------
        dict
        """
        return {
            LABEL_ID: template.identifier,
            LABEL_WORKFLOW: template.workflow_spec,
            LABEL_PARAMETERS: [p.to_dict() for p in template.parameters.values()]
        }
