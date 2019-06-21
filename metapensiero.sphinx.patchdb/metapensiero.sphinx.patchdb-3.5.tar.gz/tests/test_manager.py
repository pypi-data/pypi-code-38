# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test for PatchManager
# :Created:   mer 24 feb 2016 16:37:44 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2018, 2019 Lele Gaifax
#

from io import open
from os import unlink
from tempfile import mktemp

import pytest

from metapensiero.sphinx.patchdb.contexts import ExecutionContext
from metapensiero.sphinx.patchdb.contexts.sqlite import SQLiteContext
from metapensiero.sphinx.patchdb.manager import PatchManager, PersistentPatchManager
from metapensiero.sphinx.patchdb.patch import make_patch


def test_manager():
    ctx = ExecutionContext({'second': 1})
    pm = PatchManager()
    first = make_patch('first', 'script',
                       dict(revision=1,
                            language='test',
                            depends='second'))
    pm['first'] = first
    second = make_patch('second', 'script',
                        dict(revision=2,
                             language='test',
                             depends='third'))
    pm['second'] = second
    third = make_patch('third', 'script',
                       dict(depends='second@1',
                            preceeds='first',
                            language='test'))
    pm['third'] = third
    always_beg = make_patch('always_beg', 'script',
                            dict(always='first', language='test'))
    pm['always_beg'] = always_beg
    always_last = make_patch('always_last', 'script',
                             dict(always='last', language='test'))
    pm['always_last'] = always_last

    applied = []
    for patch in pm.neededPatches(ctx):
        if patch is not None:
            ctx.apply(patch)
            applied.append(str(patch))

    assert applied == [
        str(always_beg),
        str(third),
        str(second),
        str(first),
        str(always_last),
    ]


@pytest.mark.parametrize('suffix', ('.json', '.yaml'))
def test_persistent_patch_manager(suffix):
    tempfile = mktemp(suffix=suffix)
    pm = PersistentPatchManager(tempfile)
    first = make_patch('first', 'script',
                       dict(revision=1, language='test',
                            depends='second'),
                       'This patch costs € 0.1')
    pm['first'] = first
    second = make_patch('second', 'script',
                        dict(revision=2, language='test'))
    pm['second'] = second
    third = make_patch('third', 'script',
                       dict(depends='second@1',
                            preceeds='first',
                            language='test'))
    pm['third'] = third
    pm.save()
    with open(tempfile, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'This patch costs ' in content
    pm.load()
    assert 'This patch costs € 0.1' == pm['first'].description
    unlink(tempfile)


def test_double_jump():
    ctx = SQLiteContext(database=':memory:')

    initial_a = make_patch('table a', 'create table a (a integer)',
                           dict(revision=1,
                                language='sql'))

    ctx.apply(initial_a)

    pm = PatchManager()

    table_a = make_patch('table a', 'create table a (a integer, b integer, c integer)',
                         dict(revision=3,
                              language='sql'))
    pm += table_a

    transition_1_2 = make_patch('to table a2',
                                'alter table a add column b integer',
                                dict(revision=1,
                                     language='sql',
                                     depends='table a@1',
                                     brings='table a@2'))
    pm += transition_1_2

    transition_2_3 = make_patch('to table a3',
                                'alter table a add column c integer',
                                dict(revision=1,
                                     language='sql',
                                     depends='table a@2',
                                     brings='table a@3'))
    pm += transition_2_3

    content_table_a = make_patch('content table a',
                                 'insert into a (a,b,c) values (1,2,3)',
                                 dict(revision=1,
                                      language='sql',
                                      depends='table a@3'))
    pm += content_table_a

    applied = []
    for patch in pm.neededPatches(ctx):
        if patch is not None:
            ctx.apply(patch)
            applied.append(str(patch))

    assert applied == [
        str(transition_1_2),
        str(transition_2_3),
        str(content_table_a),
    ]
