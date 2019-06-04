#!/usr/bin/env python
#
# test_metaproc.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import random

from .. import metaproc_functions as metaproc
from .. import hierarchy
from .. import custom

from . import clear_plugins


@clear_plugins
def test_xDescriptionFromNumeric():

    custom.registerBuiltIns()

    for name in ['icd10', 'icd9', 'opcs4', 'opcs3']:

        hier = hierarchy.getHierarchyFilePath(name=name)
        hier = hierarchy.loadHierarchyFile(hier)

        code = random.choice(hier.codings)
        ncode = hierarchy.codeToNumeric(code, name)
        desc = hier.description(code)

        func = custom.get('metaproc', '{}.numdesc'.format(name))
        gendesc = func(ncode)

        assert code in gendesc
        assert desc in gendesc


@clear_plugins
def test_xDescriptionFromCode():

    custom.registerBuiltIns()

    for name in ['icd10', 'icd9', 'opcs4', 'opcs3']:
        hier = hierarchy.getHierarchyFilePath(name=name)
        hier = hierarchy.loadHierarchyFile(hier)

        code = random.choice(hier.codings)
        desc = hier.description(code)

        func = custom.get('metaproc', '{}.codedesc'.format(name))

        gendesc = func(code)

        assert code in gendesc
        assert desc in gendesc
