# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test helper functions
# :Created:   sab 28 mag 2016 20:24:52 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import unittest


class TestSplitScript(unittest.TestCase):
    def test(self):
        from metapensiero.sphinx.patchdb.contexts.sql import split_script

        self.assertEqual(split_script('a\n;;\n;;\n;;\nb\n'),
                         ['a\n', 'b\n'])

        self.assertEqual(split_script('a\n  ;;  \nb  \n\n;; \n c \n'),
                         ['a\n', 'b  \n\n', ' c \n'])


class TestIsCreateDomain(unittest.TestCase):
    def test(self):
        from metapensiero.sphinx.patchdb.contexts.sql import is_create_domain

        self.assertTrue(is_create_domain('Create Domain foo bar'))
        self.assertTrue(is_create_domain('/**/ CREATE /* asd */ Domain foo bar'))
        self.assertTrue(is_create_domain('-- foo\n\n CREATE /* asd */ Domain foo bar'))

        self.assertFalse(is_create_domain('Create Table foo bar'))

        statement = "Create Domain foo /* asd */ varchar(10)"
        iscd = is_create_domain(statement)
        name = next(iscd).value
        definition = statement[next(iscd).pos:]
        self.assertEqual(name, 'foo')
        self.assertEqual(definition, 'varchar(10)')

        statement = "Create Domain `foo` /* asd */ varchar(10)"
        iscd = is_create_domain(statement)
        name = next(iscd).value
        definition = statement[next(iscd).pos:]
        self.assertEqual(name, '`foo`')
        self.assertEqual(definition, 'varchar(10)')

        statement = 'Create Domain "TABLE" /* asd */ varchar(10)'
        iscd = is_create_domain(statement)
        name = next(iscd).value
        definition = statement[next(iscd).pos:]
        self.assertEqual(name, '"TABLE"')
        self.assertEqual(definition, 'varchar(10)')


class TestIsCreateOrAlterTable(unittest.TestCase):
    def test(self):
        from metapensiero.sphinx.patchdb.contexts.sql import is_create_or_alter_table

        self.assertTrue(is_create_or_alter_table('Create Table foo'))
        self.assertTrue(is_create_or_alter_table('/**/ CREATE /* asd */ Table foo'))
        self.assertTrue(is_create_or_alter_table('-- foo\n\n CREATE /* asd */ Table foo'))

        self.assertFalse(is_create_or_alter_table('Create Domain foo bar'))

        from metapensiero.sphinx.patchdb.contexts.sql import replace_fake_domains

        statement = "create table foo (a /* an int */ integer_t, b /* a bool */ bool_t)"
        domains = {'integer_t': 'INTEGER', 'bool_t': 'CHAR(1)'}
        isct = is_create_or_alter_table(statement)
        self.assertEqual(replace_fake_domains(statement, isct, domains),
                         "create table foo (a /* an int */ INTEGER, b /* a bool */ CHAR(1))")

        statement = 'create table foo (a INTEGER_T, b "Bool_T")'
        domains = {'integer_t': 'INTEGER', 'bool_t': 'CHAR(1)'}
        isct = is_create_or_alter_table(statement)
        self.assertEqual(replace_fake_domains(statement, isct, domains),
                         'create table foo (a INTEGER, b "Bool_T")')

        statement = 'CREATE TABLE t (v0 value_t, v1 VALUE_T, v2 "VALUE_T", v3 `Value_T`)'
        domains = {'value_t': 'X', '"VALUE_T"': 'Y', '`Value_T`': 'Z'}
        isct = is_create_or_alter_table(statement)
        self.assertEqual(replace_fake_domains(statement, isct, domains),
                         'CREATE TABLE t (v0 X, v1 X, v2 Y, v3 Z)')

        statement = 'ALTER TABLE test ADD another value_t NOT NULL'
        domains = {'value_t': 'X'}
        isct = is_create_or_alter_table(statement)
        self.assertEqual(replace_fake_domains(statement, isct, domains),
                         'ALTER TABLE test ADD another X NOT NULL')

        statement = 'ALTER TABLE t CHANGE another another value_t NULL DEFAULT NULL'
        domains = {'value_t': 'X'}
        isct = is_create_or_alter_table(statement)
        self.assertEqual(replace_fake_domains(statement, isct, domains),
                         'ALTER TABLE t CHANGE another another X NULL DEFAULT NULL')
