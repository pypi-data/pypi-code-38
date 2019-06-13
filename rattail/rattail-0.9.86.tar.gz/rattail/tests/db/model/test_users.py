# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.tests import DataTestCase


class TestUserEmailAddress(DataTestCase):

    def extra_setup(self):
        self.user = model.User(username='fred')
        self.session.add(self.user)
        self.session.flush()

    def test_email_defaults_to_none(self):
        self.assertTrue(self.user.get_email_address() is None)

    def test_email_comes_from_person_then_customer(self):
        # only customer has email at this point
        person = model.Person(first_name='Fred')
        customer = model.Customer(name='Fred')
        customer.add_email_address('customer@mailinator.com')
        customer.people.append(person)
        self.user.person = person
        self.session.flush()
        self.assertEqual(self.user.get_email_address(), 'customer@mailinator.com')

        # now person email will take preference
        person.add_email_address('person@mailinator.com')
        self.session.refresh(person)
        self.assertEqual(self.user.get_email_address(), 'person@mailinator.com')

    def test_email_address_property_works_too(self):
        # even though this may go away some day, cover it for now
        person = model.Person(first_name='Fred')
        person.add_email_address('person@mailinator.com')
        self.user.person = person
        self.session.flush()
        self.assertEqual(self.user.email_address, 'person@mailinator.com')
