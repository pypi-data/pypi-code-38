# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

import six
from mock import Mock

from rattail.db import model
from rattail.db.model import people
from rattail.tests import DataTestCase


class TestPerson(DataTestCase):

    def test_unicode(self):
        person = model.Person()
        self.assertEqual(six.text_type(person), "")

        person = model.Person(display_name="Fred Flintstone")
        self.assertEqual(six.text_type(person), "Fred Flintstone")

    # TODO: this is duplicated in TestPerson
    def test_add_email_address(self):
        person = model.Person()
        self.assertEqual(len(person.emails), 0)
        person.add_email_address('fred@mailinator.com')
        self.assertEqual(len(person.emails), 1)
        email = person.emails[0]
        self.assertEqual(email.type, 'Home')

        person = model.Person()
        self.assertEqual(len(person.emails), 0)
        person.add_email_address('fred@mailinator.com', type='Work')
        self.assertEqual(len(person.emails), 1)
        email = person.emails[0]
        self.assertEqual(email.type, 'Work')

    # TODO: this is duplicated in TestPerson
    def test_add_phone_number(self):
        person = model.Person()
        self.assertEqual(len(person.phones), 0)
        person.add_phone_number('417-555-1234')
        self.assertEqual(len(person.phones), 1)
        phone = person.phones[0]
        self.assertEqual(phone.type, 'Home')

        person = model.Person()
        self.assertEqual(len(person.phones), 0)
        person.add_phone_number('417-555-1234', type='Work')
        self.assertEqual(len(person.phones), 1)
        phone = person.phones[0]
        self.assertEqual(phone.type, 'Work')


# TODO: deprecate/remove this?
class TestFunctions(TestCase):

    def test_get_person_display_name(self):
        name = people.get_person_display_name("Fred", "Flintstone")
        self.assertEqual(name, "Fred Flintstone")

    def test_get_person_display_name_from_context(self):
        context = Mock(current_parameters={'first_name': "Fred", 'last_name': "Flintstone"})
        name = people.get_person_display_name_from_context(context)
        self.assertEqual(name, "Fred Flintstone")
