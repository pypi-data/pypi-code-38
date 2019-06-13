# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

from sqlalchemy import orm
from mock import patch, DEFAULT, Mock, MagicMock, call

from rattail import db
from rattail.db import changes, model
from rattail.tests import DataTestCase
from rattail.config import RattailConfig
from rattail.core import get_uuid


class TestRecordChangesFunc(TestCase):

    def test_session_class(self):
        Session = orm.sessionmaker()
        if hasattr(Session, 'kw'):
            self.assertRaises(KeyError, Session.kw.__getitem__, 'rattail_record_changes')
        self.assertRaises(AttributeError, getattr, Session, 'rattail_record_changes')
        changes.record_changes(Session)
        self.assertTrue(Session.rattail_record_changes)

    def test_session_instance(self):
        session = db.Session()
        self.assertFalse(session.rattail_record_changes)
        changes.record_changes(session)
        self.assertTrue(session.rattail_record_changes)
        session.close()

    def test_recorder(self):

        # no recorder
        session = db.Session()
        self.assertRaises(AttributeError, getattr, session, 'rattail_change_recorder')
        session.close()

        # default recorder
        session = db.Session()
        changes.record_changes(session)
        self.assertIs(type(session.rattail_change_recorder), changes.ChangeRecorder)
        session.close()

        # specify recorder instance
        recorder = changes.ChangeRecorder()
        session = db.Session()
        changes.record_changes(session, recorder=recorder)
        self.assertIs(session.rattail_change_recorder, recorder)
        session.close()

        # specify recorder factory
        session = db.Session()
        changes.record_changes(session, recorder=changes.ChangeRecorder)
        self.assertIs(type(session.rattail_change_recorder), changes.ChangeRecorder)
        session.close()

        # specify recorder spec via config
        config = RattailConfig()
        config.set('rattail.db', 'changes.recorder', 'rattail.db.changes:ChangeRecorder')
        session = db.Session()
        changes.record_changes(session, config=config)
        self.assertIs(type(session.rattail_change_recorder), changes.ChangeRecorder)
        session.close()

        # invalid recorder
        session = db.Session()
        self.assertRaises(ValueError, changes.record_changes, session, recorder='bogus')
        session.close()


class TestChangeRecorder(DataTestCase):

    def test_ignore_object(self):
        recorder = changes.ChangeRecorder()
        self.assertTrue(recorder.ignore_object(model.Setting()))
        self.assertTrue(recorder.ignore_object(model.Change()))
        self.assertTrue(recorder.ignore_object(model.DataSyncChange()))
        self.assertFalse(recorder.ignore_object(model.Product()))
        self.assertFalse(recorder.ignore_object(model.Customer()))

    def test_process_new_object(self):
        self.assertEqual(self.session.query(model.Change).count(), 0)
        recorder = changes.ChangeRecorder()
        product = model.Product(uuid='6de299ca178d11e6be2c3ca9f40bc550')
        recorder.process_new_object(self.session, product)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.object_key, '6de299ca178d11e6be2c3ca9f40bc550')
        self.assertFalse(change.deleted)

    def test_process_dirty_object(self):
        self.assertEqual(self.session.query(model.Change).count(), 0)
        recorder = changes.ChangeRecorder()
        product = model.Product(uuid='6de299ca178d11e6be2c3ca9f40bc550')
        recorder.process_dirty_object(self.session, product)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.object_key, '6de299ca178d11e6be2c3ca9f40bc550')
        self.assertFalse(change.deleted)

    def test_process_deleted_object(self):
        self.assertEqual(self.session.query(model.Change).count(), 0)
        recorder = changes.ChangeRecorder()
        product = model.Product(uuid='6de299ca178d11e6be2c3ca9f40bc550')
        recorder.process_deleted_object(self.session, product)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.object_key, '6de299ca178d11e6be2c3ca9f40bc550')
        self.assertTrue(change.deleted)

    def test_process_deleted_object_special(self):
        self.assertEqual(self.session.query(model.Change).count(), 0)
        recorder = changes.ChangeRecorder()

        person = model.Person(uuid='06100a34178e11e6a8633ca9f40bc550')
        for Model in (model.PersonEmailAddress, model.PersonPhoneNumber, model.PersonMailingAddress):

            self.assertEqual(self.session.query(model.Change).count(), 0)
            uuid = get_uuid()
            obj = Model(uuid=uuid, person=person)
            recorder.process_deleted_object(self.session, obj)
            self.assertEqual(self.session.query(model.Change).count(), 2)

            change = self.session.query(model.Change).filter_by(class_name=Model.__name__).one()
            self.assertEqual(change.object_key, uuid)
            self.assertTrue(change.deleted)

            change = self.session.query(model.Change).filter_by(class_name='Person').one()
            self.assertEqual(change.object_key, '06100a34178e11e6a8633ca9f40bc550')
            self.assertFalse(change.deleted)

            self.session.query(model.Change).delete(synchronize_session=False)

        employee = model.Employee(uuid='b302ac38178e11e6b8843ca9f40bc550')
        for Model in (model.EmployeeStore, model.EmployeeDepartment):

            self.assertEqual(self.session.query(model.Change).count(), 0)
            uuid = get_uuid()
            obj = Model(uuid=uuid, employee=employee)
            recorder.process_deleted_object(self.session, obj)
            self.assertEqual(self.session.query(model.Change).count(), 2)

            change = self.session.query(model.Change).filter_by(class_name=Model.__name__).one()
            self.assertEqual(change.object_key, uuid)
            self.assertTrue(change.deleted)

            change = self.session.query(model.Change).filter_by(class_name='Employee').one()
            self.assertEqual(change.object_key, 'b302ac38178e11e6b8843ca9f40bc550')
            self.assertFalse(change.deleted)

            self.session.query(model.Change).delete(synchronize_session=False)

    def test_record_change(self):
        self.assertEqual(self.session.query(model.Change).count(), 0)
        recorder = changes.ChangeRecorder()

        recorder.record_change(self.session, class_name='Bogus', object_key='bogus', deleted=False)
        self.assertEqual(self.session.query(model.Change).count(), 1)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Bogus')
        self.assertEqual(change.object_key, 'bogus')
        self.assertFalse(change.deleted)

        recorder.record_change(self.session, class_name='Invalid', object_key='invalid', deleted=True)
        self.assertEqual(self.session.query(model.Change).count(), 2)
        change = self.session.query(model.Change).filter_by(class_name='Invalid').one()
        self.assertEqual(change.object_key, 'invalid')
        self.assertTrue(change.deleted)

    def test_record_rattail_change(self):
        self.assertEqual(self.session.query(model.Change).count(), 0)
        recorder = changes.ChangeRecorder()

        # ignore change object (TODO: redundant?)
        self.assertFalse(recorder.record_rattail_change(self.session, model.Change()))
        self.assertFalse(recorder.record_rattail_change(self.session, model.DataSyncChange()))
        self.assertEqual(self.session.query(model.Change).count(), 0)

        # ignore batch object (TODO: redundant?)
        self.assertFalse(recorder.record_rattail_change(self.session, model.BatchMixin()))
        self.assertFalse(recorder.record_rattail_change(self.session, model.BatchRowMixin()))
        self.assertEqual(self.session.query(model.Change).count(), 0)

        # ignore instance with no UUID attribute
        self.assertFalse(recorder.record_rattail_change(self.session, model.Setting()))
        self.assertFalse(recorder.record_rattail_change(self.session, model.Permission()))
        self.assertEqual(self.session.query(model.Change).count(), 0)

        product = model.Product(uuid='c1b0fb94178f11e680fd3ca9f40bc550')

        # default
        self.assertTrue(recorder.record_rattail_change(self.session, product))
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.object_key, 'c1b0fb94178f11e680fd3ca9f40bc550')
        self.assertFalse(change.deleted)
        self.session.query(model.Change).delete(synchronize_session=False)

        # new
        self.assertTrue(recorder.record_rattail_change(self.session, product, type_='new'))
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.object_key, 'c1b0fb94178f11e680fd3ca9f40bc550')
        self.assertFalse(change.deleted)
        self.session.query(model.Change).delete(synchronize_session=False)

        # dirty
        self.assertTrue(recorder.record_rattail_change(self.session, product, type_='dirty'))
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.object_key, 'c1b0fb94178f11e680fd3ca9f40bc550')
        self.assertFalse(change.deleted)
        self.session.query(model.Change).delete(synchronize_session=False)

        # deleted
        self.assertTrue(recorder.record_rattail_change(self.session, product, type_='deleted'))
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.object_key, 'c1b0fb94178f11e680fd3ca9f40bc550')
        self.assertTrue(change.deleted)
        self.session.query(model.Change).delete(synchronize_session=False)


class TestChangeRecorderLegacy(TestCase):

    def test_init(self):
        recorder = changes.ChangeRecorder()

    # def test_record_change(self):
    #     session = Mock()
    #     recorder = changes.ChangeRecorder()
    #     recorder.ensure_uuid = Mock()

    #     # don't record changes for changes
    #     self.assertFalse(recorder.record_change(session, model.Change()))

    #     # don't record changes for objects with no uuid attribute
    #     self.assertFalse(recorder.record_change(session, object()))

    #     # none of the above should have involved a call to `ensure_uuid()`
    #     self.assertFalse(recorder.ensure_uuid.called)

    #     # so far no *new* changes have been created
    #     self.assertFalse(session.add.called)

    #     # mock up session to force new change creation
    #     session.query.return_value = session
    #     session.get.return_value = None
    #     self.assertTrue(recorder.record_change(session, model.Product()))

    @patch.multiple('rattail.db.changes', get_uuid=DEFAULT, object_mapper=DEFAULT)
    def test_ensure_uuid(self, get_uuid, object_mapper):
        recorder = changes.ChangeRecorder()
        uuid_column = Mock()
        object_mapper.return_value.columns.__getitem__.return_value = uuid_column

        # uuid already present
        product = model.Product(uuid='some_uuid')
        recorder.ensure_uuid(product)
        self.assertEqual(product.uuid, 'some_uuid')
        self.assertFalse(get_uuid.called)

        # no uuid yet, auto-generate
        uuid_column.foreign_keys = False
        get_uuid.return_value = 'another_uuid'
        product = model.Product()
        self.assertTrue(product.uuid is None)
        recorder.ensure_uuid(product)
        get_uuid.assert_called_once_with()
        self.assertEqual(product.uuid, 'another_uuid')

        # some heavy mocking for following tests
        uuid_column.foreign_keys = True
        remote_side = MagicMock(key='uuid')
        prop = MagicMock(__class__=orm.RelationshipProperty, key='foreign_thing')
        prop.remote_side.__len__.return_value = 1
        prop.remote_side.__iter__.return_value = [remote_side]
        object_mapper.return_value.iterate_properties.__iter__.return_value = [prop]
        
        # uuid fetched from existing foreign key object
        get_uuid.reset_mock()
        instance = Mock(uuid=None, foreign_thing=Mock(uuid='secondary_uuid'))
        recorder.ensure_uuid(instance)
        self.assertFalse(get_uuid.called)
        self.assertEqual(instance.uuid, 'secondary_uuid')

        # foreign key object doesn't exist; uuid generated as fallback
        get_uuid.return_value = 'fallback_uuid'
        instance = Mock(uuid=None, foreign_thing=None)
        recorder.ensure_uuid(instance)
        get_uuid.assert_called_once_with()
        self.assertEqual(instance.uuid, 'fallback_uuid')


class TestFunctionalChanges(DataTestCase):

    def setUp(self):
        super(TestFunctionalChanges, self).setUp()
        changes.record_changes(self.session)

    def test_add(self):
        product = model.Product()
        self.session.add(product)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.instance_uuid, product.uuid)
        self.assertFalse(change.deleted)

    def test_change(self):
        product = model.Product()
        self.session.add(product)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        product.description = 'Acme Bricks'
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.instance_uuid, product.uuid)
        self.assertFalse(change.deleted)

    def test_delete(self):
        product = model.Product()
        self.session.add(product)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        self.session.delete(product)

        self.assertEqual(self.session.query(model.Change).count(), 1)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.instance_uuid, product.uuid)
        self.assertTrue(change.deleted)

    def test_orphan_change(self):
        department = model.Department()
        subdepartment = model.Subdepartment()
        department.subdepartments.append(subdepartment)
        self.session.add(department)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 2)
        change = self.session.query(model.Change).filter_by(class_name='Department').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='Subdepartment').one()
        self.assertFalse(change.deleted)

        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        # Creating an orphaned Subdepartment, which should be recorded as a
        # *change* due to the cascade rules in effect.
        department.subdepartments.remove(subdepartment)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 2)
        change = self.session.query(model.Change).filter_by(class_name='Department').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='Subdepartment').one()
        self.assertFalse(change.deleted)
        self.assertEqual(self.session.query(model.Subdepartment).count(), 1)
    
    def test_orphan_delete(self):
        customer = model.Customer()
        group = model.CustomerGroup()
        customer.groups.append(group)
        self.session.add(customer)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 3)
        change = self.session.query(model.Change).filter_by(class_name='Customer').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='CustomerGroup').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='CustomerGroupAssignment').one()
        self.assertFalse(change.deleted)

        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        # Creating an orphaned CustomerGroupAssociation, which should be
        # recorded as a *deletion* due to the cascade rules in effect.  Note
        # that the CustomerGroup is not technically an orphan and in fact is
        # not even changed.
        customer.groups.remove(group)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 2)
        change = self.session.query(model.Change).filter_by(class_name='Customer').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='CustomerGroupAssignment').one()
        self.assertTrue(change.deleted)
        self.assertEqual(self.session.query(model.CustomerGroupAssignment).count(), 0)
