# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test the drops option
# :Created:   gio 02 nov 2017 11:28:29 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

import fixtures


FIRST = """
Initial customers table
=======================

.. patchdb:script:: Create table customers

   CREATE TABLE customers (
     id INTEGER PRIMARY KEY,
     name VARCHAR(80),
     street_address VARCHAR(80),
     city VARCHAR(80)
   )
   ;;
   INSERT INTO customers (id, name, street_address, city)
     VALUES (1, 'Lele', 'Viale Zugna', 'Rovereto')
"""


SECOND = """
Callable customers table
========================

.. patchdb:script:: Create table customers
   :revision: 2

   CREATE TABLE customers (
     id INTEGER PRIMARY KEY,
     name VARCHAR(80),
     street_address VARCHAR(80),
     city VARCHAR(80),
     telephone_number VARCHAR(80)
   )
   ;;
   INSERT INTO customers (id, name, street_address, city)
     VALUES (1, 'Lele', 'Viale Zugna', 'Rovereto)

.. patchdb:script:: Add telephone number to customers table
   :depends: Create table customers@1
   :brings: Create table customers@2

   ALTER TABLE customers ADD COLUMN telephone_number VARCHAR(80)
   ;;
   UPDATE customers SET telephone_number = '123-4567'
"""


THIRD = """
Multiple addresses
==================

.. patchdb:script:: Create table persons

   CREATE TABLE persons (
     id INTEGER PRIMARY KEY,
     name VARCHAR(80)
   )

.. patchdb:script:: Create table person_addresses
   :depends: Create table persons

   CREATE TABLE person_addresses (
     id INTEGER PRIMARY KEY,
     person_id INTEGER REFERENCES persons (id),
     street_address VARCHAR(80),
     city VARCHAR(80),
     telephone_number VARCHAR(80)
   )
   ;;

.. patchdb:script:: Migrate from customers to persons and person_addresses
   :depends:
      - Create table customers@2
      - Create table persons
      - Create table person_addresses
   :drops:
      - Create table customers
      - Add telephone number to customers table

   INSERT INTO persons (id, name) SELECT id, name FROM customers
   ;;
   INSERT INTO person_addresses (id, person_id, street_address, city, telephone_number)
     SELECT 1, id, street_address, city, telephone_number
     FROM customers
   ;;
   DROP TABLE customers
"""


class TestFinalState(fixtures.BaseTestCase):
    TEST_TXT = THIRD
    NUM_OF_SCRIPTS = 2


class TestIncremental(fixtures.BaseTestCase):
    TEST_TXT = FIRST

    def test_1(self):
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute('select telephone_number from customers')
            except exception as e:
                assert 'TELEPHONE_NUMBER' in str(e).upper()
            else:
                assert False, "Should have raised an exception of kind %r!" % exception
        finally:
            connection.close()

    def test_2(self):
        self.build({'test.txt': SECOND})
        output = self.patchdb()
        self.assertIn('Done, applied 1 script', output)
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            res = cursor.execute('select telephone_number from customers')
            assert res.fetchone()[0] == '123-4567'
            res = cursor.execute('select patchid from patchdb')
            ids = [r[0] for r in res]
            assert len(ids) == 2
            assert 'create table customers' in ids
        finally:
            connection.close()

    def test_3(self):
        self.build({'test.txt': THIRD})
        output = self.patchdb()
        self.assertIn('Done, applied 3 scripts', output)
        connection, exception = self.get_connection_and_base_exception()
        try:
            cursor = connection.cursor()
            res = cursor.execute('select telephone_number from person_addresses')
            assert res.fetchone()[0] == '123-4567'
            res = cursor.execute('select patchid from patchdb')
            ids = [r[0] for r in res]
            assert len(ids) == 3
            assert 'create table customers' not in ids
        finally:
            connection.close()
        output = self.patchdb()
        self.assertIn('Done, applied 0 scripts', output)
