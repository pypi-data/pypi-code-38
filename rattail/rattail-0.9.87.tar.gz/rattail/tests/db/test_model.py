# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

from sqlalchemy.exc import IntegrityError

from rattail.db import model
# from rattail.db.changes import record_changes
from rattail.tests import DataTestCase


class SAErrorHelper(object):

    def integrity_or_flush_error(self):
        try:
            from sqlalchemy.exc import FlushError
        except ImportError:
            return IntegrityError
        else:
            return (IntegrityError, FlushError)


class TestCustomerPerson(DataTestCase, SAErrorHelper):

    def test_customer_required(self):
        assoc = model.CustomerPerson(person=model.Person())
        self.session.add(assoc)
        self.assertRaises(self.integrity_or_flush_error(), self.session.commit)
        self.session.rollback()
        self.assertEqual(self.session.query(model.CustomerPerson).count(), 0)
        assoc.customer = model.Customer()
        self.session.add(assoc)
        self.session.commit()
        self.assertEqual(self.session.query(model.CustomerPerson).count(), 1)

    def test_person_required(self):
        assoc = model.CustomerPerson(customer=model.Customer())
        self.session.add(assoc)
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.assertEqual(self.session.query(model.CustomerPerson).count(), 0)
        assoc.person = model.Person()
        self.session.add(assoc)
        self.session.commit()
        self.assertEqual(self.session.query(model.CustomerPerson).count(), 1)

    def test_ordinal_autoincrement(self):
        customer = model.Customer()
        self.session.add(customer)
        assoc = model.CustomerPerson(person=model.Person())
        customer._people.append(assoc)
        self.session.commit()
        self.assertEqual(assoc.ordinal, 1)
        assoc = model.CustomerPerson(person=model.Person())
        customer._people.append(assoc)
        self.session.commit()
        self.assertEqual(assoc.ordinal, 2)


class TestCustomerGroupAssignment(DataTestCase, SAErrorHelper):

    def test_customer_required(self):
        assignment = model.CustomerGroupAssignment(group=model.CustomerGroup())
        self.session.add(assignment)
        self.assertRaises(self.integrity_or_flush_error(), self.session.commit)
        self.session.rollback()
        self.assertEqual(self.session.query(model.CustomerGroupAssignment).count(), 0)
        assignment.customer = model.Customer()
        self.session.add(assignment)
        self.session.commit()
        self.assertEqual(self.session.query(model.CustomerGroupAssignment).count(), 1)

    def test_group_required(self):
        assignment = model.CustomerGroupAssignment(customer=model.Customer())
        self.session.add(assignment)
        self.assertRaises(IntegrityError, self.session.commit)
        self.session.rollback()
        self.assertEqual(self.session.query(model.CustomerGroupAssignment).count(), 0)
        assignment.group = model.CustomerGroup()
        self.session.add(assignment)
        self.session.commit()
        self.assertEqual(self.session.query(model.CustomerGroupAssignment).count(), 1)

    def test_ordinal_autoincrement(self):
        customer = model.Customer()
        self.session.add(customer)
        assignment = model.CustomerGroupAssignment(group=model.CustomerGroup())
        customer._groups.append(assignment)
        self.session.commit()
        self.assertEqual(assignment.ordinal, 1)
        assignment = model.CustomerGroupAssignment(group=model.CustomerGroup())
        customer._groups.append(assignment)
        self.session.commit()
        self.assertEqual(assignment.ordinal, 2)


# class TestCustomerEmailAddress(DataTestCase):

#     def test_pop(self):
#         customer = model.Customer()
#         customer.add_email_address('fred.home@mailinator.com')
#         customer.add_email_address('fred.work@mailinator.com')
#         self.session.add(customer)
#         self.session.commit()
#         self.assertEqual(self.session.query(model.Customer).count(), 1)
#         self.assertEqual(self.session.query(model.CustomerEmailAddress).count(), 2)

#         while customer.emails:
#             customer.emails.pop()
#         self.session.commit()
#         self.assertEqual(self.session.query(model.Customer).count(), 1)
#         self.assertEqual(self.session.query(model.CustomerEmailAddress).count(), 0)

#         # changes weren't being recorded
#         self.assertEqual(self.session.query(model.Change).count(), 0)

#     def test_pop_with_changes(self):
#         record_changes(self.session)

#         customer = model.Customer()
#         customer.add_email_address('fred.home@mailinator.com')
#         customer.add_email_address('fred.work@mailinator.com')
#         self.session.add(customer)
#         self.session.commit()
#         self.assertEqual(self.session.query(model.Customer).count(), 1)
#         self.assertEqual(self.session.query(model.CustomerEmailAddress).count(), 2)

#         while customer.emails:
#             customer.emails.pop()
#         self.session.commit()
#         self.assertEqual(self.session.query(model.Customer).count(), 1)
#         self.assertEqual(self.session.query(model.CustomerEmailAddress).count(), 0)

#         # changes should have been recorded
#         changes = self.session.query(model.Change)
#         self.assertEqual(changes.count(), 3)

#         customer_change = changes.filter_by(class_name='Customer').one()
#         self.assertEqual(customer_change.uuid, customer.uuid)
#         self.assertFalse(customer_change.deleted)

#         email_changes = changes.filter_by(class_name='CustomerEmailAddress')
#         self.assertEqual(email_changes.count(), 2)
#         self.assertEqual([x.deleted for x in email_changes], [True, True])


class TestLabelProfile(DataTestCase):

    def test_get_printer_setting(self):
        profile = model.LabelProfile()
        self.session.add(profile)

        self.assertTrue(profile.uuid is None)
        setting = profile.get_printer_setting('some_setting')
        self.assertTrue(setting is None)
        self.assertTrue(profile.uuid is None)

        profile.uuid = 'some_uuid'
        self.session.add(model.Setting(
                name='labels.some_uuid.printer.some_setting',
                value='some_value'))
        self.session.flush()
        setting = profile.get_printer_setting('some_setting')
        self.assertEquals(setting, 'some_value')

    def test_save_printer_setting(self):
        self.assertEqual(self.session.query(model.Setting).count(), 0)
        profile = model.LabelProfile()
        self.session.add(profile)

        self.assertTrue(profile.uuid is None)
        profile.save_printer_setting('some_setting', 'some_value')
        self.assertFalse(profile.uuid is None)
        self.assertEqual(self.session.query(model.Setting).count(), 1)

        profile.uuid = 'some_uuid'
        profile.save_printer_setting('some_setting', 'some_value')
        self.assertEqual(self.session.query(model.Setting).count(), 2)
        setting = self.session.query(model.Setting)\
            .filter_by(name='labels.some_uuid.printer.some_setting')\
            .one()
        self.assertEqual(setting.value, 'some_value')
