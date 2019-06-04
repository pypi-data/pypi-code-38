#!/usr/bin/env python
#
# metaproc_functions.py - Functions for manipulating column metadata.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains ``metaproc`` functions - functions for manipulating
column metadata.

Some :class:`.Column` instances have a ``metadata`` attribute, containing some
additional information about the column. The functions in this module can be
used to modify these metadata values. Currently, column metadata is only used
to generate a description of each column (via the ``--description_file``
command-line option).
"""


from . import custom
from . import hierarchy


def hierarchicalDescriptionFromNumeric(val, name):
    """Generates a description for a numeric hierarchical code. """
    val  = hierarchy.numericToCode(val, name)
    hier = hierarchy.getHierarchyFilePath(name=name)
    hier = hierarchy.loadHierarchyFile(hier)
    desc = hier.description(val)
    return '{} - {}'.format(val, desc)


def hierarchicalDescriptionFromCode(val, name):
    """Generates a description for a hierarchical code. """
    hier = hierarchy.getHierarchyFilePath(name=name)
    hier = hierarchy.loadHierarchyFile(hier)
    desc = hier.description(val)
    return '{} - {}'.format(val, desc)


@custom.metaproc('icd10.numdesc')
def icd10DescriptionFromNumeric(val):
    """Generates a description for a numeric ICD10 code. """
    return hierarchicalDescriptionFromNumeric(val, 'icd10')


@custom.metaproc('icd10.codedesc')
def icd10DescriptionFromCode(val):
    """Generates a description for an ICD10 code. """
    return hierarchicalDescriptionFromCode(val, 'icd10')


@custom.metaproc('icd9.numdesc')
def icd9DescriptionFromNumeric(val):
    """Generates a description for a numeric ICD9 code. """
    return hierarchicalDescriptionFromNumeric(val, 'icd9')


@custom.metaproc('icd9.codedesc')
def icd9DescriptionFromCode(val):
    """Generates a description for an ICD9 code. """
    return hierarchicalDescriptionFromCode(val, 'icd9')


@custom.metaproc('opcs4.numdesc')
def opcs4DescriptionFromNumeric(val):
    """Generates a description for a numeric OPCS4 code. """
    return hierarchicalDescriptionFromNumeric(val, 'opcs4')


@custom.metaproc('opcs4.codedesc')
def opcs4DescriptionFromCode(val):
    """Generates a description for an OPCS4 code. """
    return hierarchicalDescriptionFromCode(val, 'opcs4')


@custom.metaproc('opcs3.numdesc')
def opcs3DescriptionFromNumeric(val):
    """Generates a description for a numeric OPCS3 code. """
    return hierarchicalDescriptionFromNumeric(val, 'opcs3')


@custom.metaproc('opcs3.codedesc')
def opcs3DescriptionFromCode(val):
    """Generates a description for an OPCS3 code. """
    return hierarchicalDescriptionFromCode(val, 'opcs3')
