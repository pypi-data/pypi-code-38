# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Rattail Model Importers
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

import six
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound

from rattail.db import model, auth
from rattail.importing import ToSQLAlchemy, BatchImporter
from rattail.db.util import maxlen, normalize_full_name, format_phone_number, normalize_phone_number
from rattail.time import localtime, make_utc


log = logging.getLogger(__name__)


class ToRattail(ToSQLAlchemy):
    """
    Base class for all Rattail model importers.
    """
    key = 'uuid'
    extension_attr = None
    extension_fields = []

    @property
    def simple_fields(self):
        return super(ToRattail, self).simple_fields + self.extension_fields

    def cache_query_options(self):
        options = super(ToRattail, self).cache_query_options() or []
        # eager join extension table if applicable
        if self.extension_attr and self.fields_active(self.extension_fields):
            options.append(orm.joinedload(getattr(self.model_class, self.extension_attr)))
        return options

    def normalize_local_object(self, obj):
        data = super(ToRattail, self).normalize_local_object(obj)
        if data and self.extension_fields:
            for field in self.extension_fields:
                if field in self.fields:
                    data[field] = getattr(obj, field)
        return data

    def update_object(self, obj, host_data, local_data=None):
        obj = super(ToRattail, self).update_object(obj, host_data, local_data)
        if obj and self.extension_fields:
            for field in self.extension_fields:
                if field in self.fields:
                    if not local_data or field not in local_data or local_data[field] != host_data[field]:
                        setattr(obj, field, host_data[field])
        return obj


class PersonImporter(ToRattail):
    """
    Person data importer.
    """
    model_class = model.Person


class PersonEmailAddressImporter(ToRattail):
    """
    Person email address data importer.
    """
    model_class = model.PersonEmailAddress

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'preferred',
        ]

    def normalize_local_object(self, email):
        data = super(PersonEmailAddressImporter, self).normalize_local_object(email)
        if 'preferred' in self.fields:
            data['preferred'] = email.preference == 1
        return data

    def update_object(self, email, data, local_data=None):
        email = super(PersonEmailAddressImporter, self).update_object(email, data, local_data)
        if 'preferred' in self.fields:
            if data['preferred']:
                if email.preference != 1:
                    person = email.person
                    if not person:
                        person = self.session.query(model.Person).get(email.parent_uuid)
                    if email in person.emails:
                        person.emails.remove(email)
                    person.emails.insert(0, email)
                    person.emails.reorder()
            else:
                if email.preference == 1:
                    person = email.person
                    if not person:
                        person = self.session.query(model.Person).get(email.parent_uuid)
                    if len(person.emails) > 1:
                        person.emails.remove(email)
                        person.emails.append(email)
                        person.emails.reorder()

        # If this is a new record, we may still need to establish its preference.
        if email.preference is None:
            person = email.person
            if not person:
                person = self.session.query(model.Person).get(email.parent_uuid)
            if email not in person.emails:
                person.emails.append(email)
            person.emails.reorder()

        return email


class PersonPhoneNumberImporter(ToRattail):
    """
    Person phone number data importer.
    """
    model_class = model.PersonPhoneNumber

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'normalized_number',
            'preferred',
        ]

    def format_number(self, number):
        return format_phone_number(number)

    def normalize_number(self, number):
        return normalize_phone_number(number)

    def normalize_local_object(self, phone):
        data = super(PersonPhoneNumberImporter, self).normalize_local_object(phone)
        if 'normalized_number' in self.fields:
            data['normalized_number'] = self.normalize_number(phone.number)
        if 'preferred' in self.fields:
            data['preferred'] = phone.preference == 1
        return data

    def update_object(self, phone, data, local_data=None):
        phone = super(PersonPhoneNumberImporter, self).update_object(phone, data, local_data)
        if 'preferred' in self.fields:
            if data['preferred']:
                if phone.preference != 1:
                    person = phone.person
                    if not person:
                        person = self.session.query(model.Person).get(phone.parent_uuid)
                    if phone in person.phones:
                        person.phones.remove(phone)
                    person.phones.insert(0, phone)
                    person.phones.reorder()
            else:
                if phone.preference == 1:
                    person = phone.person
                    if not person:
                        person = self.session.query(model.Person).get(phone.parent_uuid)
                    if len(person.phones) > 1:
                        person.phones.remove(phone)
                        person.phones.append(phone)
                        person.phones.reorder()

        # If this is a new record, we may still need to establish its preference.
        if phone.preference is None:
            person = phone.person
            if not person:
                person = self.session.query(model.Person).get(phone.parent_uuid)
            if phone not in person.phones:
                person.phones.append(phone)
            person.phones.reorder()

        return phone


class PersonMailingAddressImporter(ToRattail):
    """
    Person mailing address data importer.
    """
    model_class = model.PersonMailingAddress


class PersonNoteImporter(ToRattail):
    """
    Person notes data importer.
    """
    model_class = model.PersonNote


class UserImporter(ToRattail):
    """
    User data importer.
    """
    model_class = model.User

    @property
    def supported_fields(self):
        return super(UserImporter, self).supported_fields + ['plain_password']

    def normalize_local_object(self, user):
        data = super(UserImporter, self).normalize_local_object(user)
        if 'plain_password' in self.fields:
            data['plain_password'] = None # can't decrypt stored password
        return data

    def update_object(self, user, data, local_data=None):
        from rattail.db import auth

        user = super(UserImporter, self).update_object(user, data, local_data)
        if user:
            if 'plain_password' in self.fields:
                if data['plain_password']:
                    auth.set_user_password(user, data['plain_password'])
            return user


class AdminUserImporter(UserImporter):
    """
    User data importer, plus 'admin' boolean field.
    """

    @property
    def supported_fields(self):
        return super(AdminUserImporter, self).supported_fields + ['admin']

    def setup(self):
        super(AdminUserImporter, self).setup()
        self.admin_uuid = auth.administrator_role(self.session).uuid

    def cache_query_options(self):
        options = super(AdminUserImporter, self).cache_query_options()
        if 'admin' in self.fields:
            options.append(orm.joinedload(model.User._roles))
        return options

    def get_admin(self, session=None):
        from rattail.db import auth
        return auth.administrator_role(session or self.session)

    def normalize_local_object(self, user):
        data = super(AdminUserImporter, self).normalize_local_object(user)
        if 'admin' in self.fields:
            data['admin'] = self.admin_uuid in [r.role_uuid for r in user._roles]
        return data

    def update_object(self, user, data, local_data=None):
        user = super(AdminUserImporter, self).update_object(user, data, local_data)
        if user:
            if 'admin' in self.fields:
                admin = self.get_admin()
                if data['admin']:
                    if admin not in user.roles:
                        user.roles.append(admin)
                else:
                    if admin in user.roles:
                        user.roles.remove(admin)
            return user


class MessageImporter(ToRattail):
    """
    User message data importer.
    """
    model_class = model.Message


class MessageRecipientImporter(ToRattail):
    """
    User message recipient data importer.
    """
    model_class = model.MessageRecipient


class StoreImporter(ToRattail):
    """
    Store data importer.
    """
    model_class = model.Store

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'phone_number',
            'fax_number',
        ]

    def cache_query_options(self):
        if 'phone_number' in self.fields or 'fax_number' in self.fields:
            return [orm.joinedload(model.Store.phones)]

    def normalize_local_object(self, store):
        data = super(StoreImporter, self).normalize_local_object(store)

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in store.phones:
                if phone.type == 'Voice':
                    data['phone_number'] = phone.number
                    break

        if 'fax_number' in self.fields:
            data['fax_number'] = None
            for phone in store.phones:
                if phone.type == 'Fax':
                    data['fax_number'] = phone.number
                    break

        return data

    def update_object(self, store, data, local_data=None):
        store = super(StoreImporter, self).update_object(store, data, local_data)

        if 'phone_number' in self.fields:
            number = data['phone_number'] or None
            if number:
                found = False
                for phone in store.phones:
                    if phone.type == 'Voice':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    store.add_phone_number(number, type='Voice')
            else:
                for phone in list(store.phones):
                    if phone.type == 'Voice':
                        store.phones.remove(phone)

        if 'fax_number' in self.fields:
            number = data['fax_number'] or None
            if number:
                found = False
                for phone in store.phones:
                    if phone.type == 'Fax':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    store.add_phone_number(number, type='Fax')
            else:
                for phone in list(store.phones):
                    if phone.type == 'Fax':
                        store.phones.remove(phone)

        return store


class StorePhoneNumberImporter(ToRattail):
    """
    Store phone data importer.
    """
    model_class = model.StorePhoneNumber


class EmployeeImporter(ToRattail):
    """
    Employee data importer.
    """
    model_class = model.Employee
    person_fields = [
        'first_name',
        'last_name',
        'full_name',
    ]
    phone_fields = [
        'phone_number',
        'phone_number_2',
    ]

    @property
    def supported_fields(self):
        return self.simple_fields + self.person_fields + self.phone_fields + [
            'customer_id',
            'email_address',
        ]

    def setup(self):
        if 'customer_id' in self.fields:
            self.customers = self.cache_model(model.Customer, key='id')

    def cache_query_options(self):
        options = []
        if self.fields_active(self.person_fields):
            options.append(orm.joinedload(model.Employee.person))
        if self.fields_active(self.phone_fields):
            options.append(orm.joinedload(model.Employee.phones))
        if 'customer_id' in self.fields:
            options.append(orm.joinedload(model.Employee.person)\
                           .joinedload(model.Person._customers))
        if 'email_address' in self.fields:
            options.append(orm.joinedload(model.Employee.email))
        return options

    def normalize_local_object(self, employee):
        data = super(EmployeeImporter, self).normalize_local_object(employee)

        if self.fields_active(self.person_fields + ['customer_id']):
            person = employee.person
            if 'first_name' in self.fields:
                data['first_name'] = person.first_name
            if 'last_name' in self.fields:
                data['last_name'] = person.last_name
            if 'full_name' in self.fields:
                data['full_name'] = person.display_name
            if 'customer_id' in self.fields:
                customer = person.customers[0] if person.customers else None
                data['customer_id'] = customer.id if customer else None

        if 'phone_number' in self.fields:
            data['phone_number'] = None
            for phone in employee.phones:
                if phone.type == 'Home':
                    data['phone_number'] = phone.number
                    break

        if 'phone_number_2' in self.fields:
            data['phone_number_2'] = None
            first = False
            for phone in employee.phones:
                if phone.type == 'Home':
                    if first:
                        data['phone_number_2'] = phone.number
                        break
                    first = True

        if 'email_address' in self.fields:
            email = employee.email
            data['email_address'] = email.address if email else None

        return data

    def get_customer(self, customer_id):
        if hasattr(self, 'customers'):
            return self.customers.get(customer_id)
        return self.session.query(model.Customer)\
                           .filter(model.Customer.id == customer_id)\
                           .first()

    def update_object(self, employee, data, local_data=None):
        employee = super(EmployeeImporter, self).update_object(employee, data, local_data)

        if self.fields_active(self.person_fields):
            person = employee.person
            if not person:
                self.session.flush()
                if not employee.person:
                    log.debug("creating new Person for Employee with data: {}".format(data))
                    employee.person = model.Person()
                person = employee.person
            if 'first_name' in self.fields and person.first_name != data['first_name']:
                person.first_name = data['first_name']
            if 'last_name' in self.fields and person.last_name != data['last_name']:
                person.last_name = data['last_name']
            if 'full_name' in self.fields and person.display_name != data['full_name']:
                person.display_name = data['full_name']

        if 'customer_id' in self.fields:
            customer_id = data['customer_id']
            if customer_id:
                customer = self.get_customer(customer_id)
                if not customer:
                    customer = model.Customer()
                    customer.id = customer_id
                    customer.name = employee.display_name
                    self.session.add(customer)
                    if hasattr(self, 'customers'):
                        self.customers[customer.id] = customer
                if person not in customer.people:
                    customer.people.append(person)
            else:
                del person.customers[:]

        if 'phone_number' in self.fields:
            phones = [phone for phone in employee.phones if phone.type == 'Home']
            number = data['phone_number']
            if number:
                if phones:
                    phone = phones[0]
                    if phone.number != number:
                        phone.number = number
                else:
                    employee.add_phone_number(number, type='Home')
            else:
                for phone in phones:
                    employee.phones.remove(phone)

        if 'phone_number_2' in self.fields:
            phones = [phone for phone in employee.phones if phone.type == 'Home']
            number = data['phone_number_2']
            if number:
                if len(phones) > 1:
                    phone = phones[1]
                    if phone.number != number:
                        phone.number = number
                else:
                    employee.add_phone_number(number, 'Home')
            else:
                for phone in phones[1:]:
                    employee.phones.remove(phone)

        if 'email_address' in self.fields:
            address = data['email_address']
            if address:
                if employee.email:
                    if employee.email.address != address:
                        employee.email.address = address
                else:
                    employee.add_email_address(address)
            elif employee.email:
                del employee.emails[:]

        return employee


class EmployeeStoreImporter(ToRattail):
    """
    Employee/store data importer.
    """
    model_class = model.EmployeeStore


class EmployeeDepartmentImporter(ToRattail):
    """
    Employee/department data importer.
    """
    model_class = model.EmployeeDepartment


class EmployeeEmailAddressImporter(ToRattail):
    """
    Employee email data importer.
    """
    model_class = model.EmployeeEmailAddress


class EmployeePhoneNumberImporter(ToRattail):
    """
    Employee phone data importer.
    """
    model_class = model.EmployeePhoneNumber


class EmployeeHistoryImporter(ToRattail):
    """
    Employee history data importer
    """
    model_class = model.EmployeeHistory


class ScheduledShiftImporter(ToRattail):
    """
    Imports employee scheduled shifts.
    """
    model_class = model.ScheduledShift


class WorkedShiftImporter(ToRattail):
    """
    Imports shifts worked by employees.
    """
    model_class = model.WorkedShift


class CustomerImporter(ToRattail):
    """
    Customer data importer.
    """
    model_class = model.Customer
    person_fields = [
        'person_uuid',
        'first_name',
        'last_name',
    ]
    phone_fields = [
        'phone_number',
        'phone_number_2',
    ]
    address_fields = [
        'address_street',
        'address_street2',
        'address_city',
        'address_state',
        'address_zipcode',
        'address_invalid',
    ]
    group_fields = [
        'group_id',
        'group_id_2',
    ]

    @property
    def supported_fields(self):
        return self.simple_fields + self.person_fields + self.phone_fields + self.address_fields + self.group_fields + [
            'email_address',
        ]

    def setup(self):
        if self.fields_active(self.group_fields):
            self.groups = self.cache_model(model.CustomerGroup, key='id')

    def cache_query_options(self):
        options = []
        if self.fields_active(self.person_fields):
            options.append(orm.joinedload(model.Customer._people)\
                           .joinedload(model.CustomerPerson.person))
        if self.fields_active(self.phone_fields):
            options.append(orm.joinedload(model.Customer.phones))
        if self.fields_active(self.address_fields):
            options.append(orm.joinedload(model.Customer.addresses))
        if 'email_address' in self.fields:
            options.append(orm.joinedload(model.Customer.email))
        if self.fields_active(self.group_fields):
            options.append(orm.joinedload(model.Customer._groups)\
                           .joinedload(model.CustomerGroupAssignment.group))
        return options

    def normalize_local_object(self, customer):
        data = super(CustomerImporter, self).normalize_local_object(customer)
        if self.fields_active(self.person_fields):
            person = customer.people[0] if customer.people else None
            if 'person_uuid' in self.fields:
                data['person_uuid'] = person.uuid if person else None
            if 'first_name' in self.fields:
                data['first_name'] = person.first_name if person else None
            if 'last_name' in self.fields:
                data['last_name'] = person.last_name if person else None

        if self.fields_active(self.phone_fields):
            phones = [phone for phone in customer.phones if phone.type == 'Voice']
            if 'phone_number' in self.fields:
                data['phone_number'] = phones[0].number if phones else None
            if 'phone_number_2' in self.fields:
                data['phone_number_2'] = phones[1].number if len(phones) > 1 else None

        if 'email_address' in self.fields:
            email = customer.email
            data['email_address'] = email.address if email else None

        if self.fields_active(self.address_fields):
            address = customer.addresses[0] if customer.addresses else None
            for field in self.address_fields:
                if field in self.fields:
                    if address:
                        data[field] = getattr(address, field[8:])
                    else:
                        data[field] = None

        if 'group_id' in self.fields:
            group = customer.groups[0] if customer.groups else None
            data['group_id'] = group.id if group else None

        if 'group_id_2' in self.fields:
            group = customer.groups[1] if customer.groups and len(customer.groups) > 1 else None
            data['group_id_2'] = group.id if group else None

        return data

    def get_group(self, group_id):
        if hasattr(self, 'groups'):
            return self.groups.get(group_id)
        return self.session.query(model.CustomerGroup)\
                           .filter(model.CustomerGroup.id == group_id)\
                           .first()

    def update_object(self, customer, data, local_data=None):
        customer = super(CustomerImporter, self).update_object(customer, data, local_data)

        if self.fields_active(self.person_fields):
            new_person = False
            if not customer.people:
                new_person = True
                if 'person_uuid' in self.fields:
                    customer._people.append(model.CustomerPerson(person_uuid=data['person_uuid']))
                else:
                    customer.people.append(model.Person())
            person = customer.people[0]
            if 'first_name' in self.fields and person.first_name != data['first_name']:
                person.first_name = data['first_name']
            if 'last_name' in self.fields and person.last_name != data['last_name']:
                person.last_name = data['last_name']
            if new_person and 'first_name' in self.fields and 'last_name' in self.fields:
                person.display_name = normalize_full_name(person.first_name, person.last_name)

        if 'phone_number' in self.fields:
            phones = [phone for phone in customer.phones if phone.type == 'Voice']
            number = data['phone_number']
            if number:
                if phones:
                    phone = phones[0]
                    if phone.number != number:
                        phone.number = number
                else:
                    customer.add_phone_number(number, type='Voice')
            else:
                for phone in phones:
                    customer.phones.remove(phone)

        if 'phone_number_2' in self.fields:
            phones = [phone for phone in customer.phones if phone.type == 'Voice']
            number = data['phone_number_2']
            if number:
                if len(phones) > 1:
                    phone = phones[1]
                    if phone.number != number:
                        phone.number = number
                else:
                    customer.add_phone_number(number, 'Voice')
            else:
                for phone in phones[1:]:
                    customer.phones.remove(phone)

        if 'email_address' in self.fields:
            address = data['email_address']
            if address:
                if customer.email:
                    if customer.email.address != address:
                        customer.email.address = address
                else:
                    customer.add_email_address(address)
            else:
                if len(customer.emails):
                    del customer.emails[:]

        if self.fields_active(self.address_fields):
            if any([data[f] for f in self.address_fields if f in self.fields]):
                if customer.addresses:
                    address = customer.addresses[0]
                else:
                    address = model.CustomerMailingAddress()
                    customer.addresses.append(address)
                for field in self.address_fields:
                    if field in self.fields:
                        if getattr(address, field[8:]) != data[field]:
                            setattr(address, field[8:], data[field])
            elif customer.addresses:
                customer.addresses.pop(0)

        if 'group_id' in self.fields:
            group_id = data['group_id']
            if group_id:
                group = self.get_group(group_id)
                if not group:
                    group = model.CustomerGroup()
                    group.id = group_id
                    group.name = "(auto-created)"
                    self.session.add(group)
                    if hasattr(self, 'groups'):
                        self.groups[group.id] = group
                if group in customer.groups:
                    if group is not customer.groups[0]:
                        customer.groups.remove(group)
                        customer.groups.insert(0, group)
                else:
                    customer.groups.insert(0, group)
            elif customer.groups:
                del customer.groups[:]

        if 'group_id_2' in self.fields:
            group_id = data['group_id_2']
            if group_id:
                group = self.get_group(group_id)
                if not group:
                    group = model.CustomerGroup()
                    group.id = group_id
                    group.name = "(auto-created)"
                    self.session.add(group)
                    if hasattr(self, 'groups'):
                        self.groups[group.id] = group
                if group in customer.groups:
                    if len(customer.groups) > 1:
                        if group is not customer.groups[1]:
                            customer.groups.remove(group)
                            customer.groups.insert(1, group)
                else:
                    if len(customer.groups) > 1:
                        customer.groups.insert(1, group)
                    else:
                        customer.groups.append(group)
            elif len(customer.groups) > 1:
                del customer.groups[1:]

        return customer


class CustomerGroupImporter(ToRattail):
    """
    CustomerGroup data importer.
    """
    model_class = model.CustomerGroup


class CustomerGroupAssignmentImporter(ToRattail):
    """
    CustomerGroupAssignment data importer.
    """
    model_class = model.CustomerGroupAssignment


class CustomerPersonImporter(ToRattail):
    """
    CustomerPerson data importer.
    """
    model_class = model.CustomerPerson


class CustomerEmailAddressImporter(ToRattail):
    """
    Customer email address data importer.
    """
    model_class = model.CustomerEmailAddress


class CustomerPhoneNumberImporter(ToRattail):
    """
    Customer phone number data importer.
    """
    model_class = model.CustomerPhoneNumber


class MemberImporter(ToRattail):
    """
    Member data importer.
    """
    model_class = model.Member


class MemberEmailAddressImporter(ToRattail):
    """
    Member email address data importer.
    """
    model_class = model.MemberEmailAddress


class MemberPhoneNumberImporter(ToRattail):
    """
    Member phone number data importer.
    """
    model_class = model.MemberPhoneNumber


class VendorImporter(ToRattail):
    """
    Vendor data importer.
    """
    model_class = model.Vendor
    phone_fields = [
        'phone_number',
        'phone_number_2',
    ]
    fax_fields = [
        'fax_number',
        'fax_number_2',
    ]
    contact_fields = [
        'contact_name',
        'contact_name_2',
    ]

    @property
    def supported_fields(self):
        return self.simple_fields + self.phone_fields + self.fax_fields + self.contact_fields + [
            'email_address',
        ]

    def cache_query(self):
        query = super(VendorImporter, self).cache_query()
        if len(self.key) == 1 and self.key[0] == 'id':
            query = query.filter(model.Vendor.id != None)
        return query

    def cache_query_options(self):
        options = []
        if self.fields_active(self.phone_fields + self.fax_fields):
            options.append(orm.joinedload(model.Vendor.phones))
        if self.fields_active(self.contact_fields):
            options.append(orm.joinedload(model.Vendor._contacts))
        if 'email_address' in self.fields:
            options.append(orm.joinedload(model.Vendor.email))
        return options

    def normalize_local_object(self, vendor):
        data = super(VendorImporter, self).normalize_local_object(vendor)

        if self.fields_active(self.phone_fields):
            phones = [phone for phone in vendor.phones if phone.type == 'Voice']
            if 'phone_number' in self.fields:
                data['phone_number'] = phones[0].number if phones else None
            if 'phone_number_2' in self.fields:
                data['phone_number_2'] = phones[1].number if len(phones) > 1 else None

        if self.fields_active(self.fax_fields):
            phones = [phone for phone in vendor.phones if phone.type == 'Fax']
            if 'fax_number' in self.fields:
                data['fax_number'] = phones[0].number if phones else None
            if 'fax_number_2' in self.fields:
                data['fax_number_2'] = phones[1].number if len(phones) > 1 else None

        if 'contact_name' in self.fields:
            contact = vendor.contact
            data['contact_name'] = contact.display_name if contact else None

        if 'contact_name_2' in self.fields:
            contact = vendor.contacts[1] if len(vendor.contacts) > 1 else None
            data['contact_name_2'] = contact.display_name if contact else None

        if 'email_address' in self.fields:
            email = vendor.email
            data['email_address'] = email.address if email else None

        return data

    def update_object(self, vendor, data, local_data=None):
        vendor = super(VendorImporter, self).update_object(vendor, data, local_data)

        if 'phone_number' in self.fields:
            number = data['phone_number'] or None
            if number:
                found = False
                for phone in vendor.phones:
                    if phone.type == 'Voice':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    vendor.add_phone_number(number, type='Voice')
            else:
                for phone in list(vendor.phones):
                    if phone.type == 'Voice':
                        vendor.phones.remove(phone)

        if 'phone_number_2' in self.fields:
            number = data['phone_number_2'] or None
            if number:
                found = False
                first = False
                for phone in vendor.phones:
                    if phone.type == 'Voice':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    vendor.add_phone_number(number, type='Voice')
            else:
                first = False
                for phone in list(vendor.phones):
                    if phone.type == 'Voice':
                        if first:
                            vendor.phones.remove(phone)
                            break
                        first = True

        if 'fax_number' in self.fields:
            number = data['fax_number'] or None
            if number:
                found = False
                for phone in vendor.phones:
                    if phone.type == 'Fax':
                        if phone.number != number:
                            phone.number = number
                        found = True
                        break
                if not found:
                    vendor.add_phone_number(number, type='Fax')
            else:
                for phone in list(vendor.phones):
                    if phone.type == 'Fax':
                        vendor.phones.remove(phone)

        if 'fax_number_2' in self.fields:
            number = data['fax_number_2'] or None
            if number:
                found = False
                first = False
                for phone in vendor.phones:
                    if phone.type == 'Fax':
                        if first:
                            if phone.number != number:
                                phone.number = number
                            found = True
                            break
                        first = True
                if not found:
                    vendor.add_phone_number(number, type='Fax')
            else:
                first = False
                for phone in list(vendor.phones):
                    if phone.type == 'Fax':
                        if first:
                            vendor.phones.remove(phone)
                            break
                        first = True

        if 'contact_name' in self.fields:
            if data['contact_name']:
                contact = vendor.contact
                if not contact:
                    contact = model.Person()
                    self.session.add(contact)
                    vendor.contacts.append(contact)
                contact.display_name = data['contact_name']
            elif vendor.contacts:
                del vendor.contacts[:]

        if 'contact_name_2' in self.fields:
            if data['contact_name_2']:
                contact = vendor.contacts[1] if len(vendor.contacts) > 1 else None
                if not contact:
                    contact = model.Person()
                    self.session.add(contact)
                    vendor.contacts.append(contact)
                contact.display_name = data['contact_name_2']
            elif len(vendor.contacts) > 1:
                del vendor.contacts[1:]

        if 'email_address' in self.fields:
            address = data['email_address'] or None
            if address:
                if vendor.email:
                    if vendor.email.address != address:
                        vendor.email.address = address
                else:
                    vendor.add_email_address(address)
            elif vendor.emails:
                del vendor.emails[:]

        return vendor


class VendorEmailAddressImporter(ToRattail):
    """
    Vendor email data importer.
    """
    model_class = model.VendorEmailAddress


class VendorPhoneNumberImporter(ToRattail):
    """
    Vendor phone data importer.
    """
    model_class = model.VendorPhoneNumber


class VendorContactImporter(ToRattail):
    """
    Vendor contact data importer.
    """
    model_class = model.VendorContact


class DepartmentImporter(ToRattail):
    """
    Department data importer.
    """
    model_class = model.Department

    def cache_query(self):
        query = self.session.query(model.Department)
        if 'number' in self.key:
            query = query.filter(model.Department.number != None)
        return query


class SubdepartmentImporter(ToRattail):
    """
    Subdepartment data importer.
    """
    model_class = model.Subdepartment

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'department_number',
        ]

    def setup(self):
        if 'department_number' in self.fields:
            query = self.session.query(model.Department)\
                                .filter(model.Department.number != None)
            self.departments = self.cache_model(model.Department, key='number', query=query)

    def cache_query_options(self):
        options = []
        if 'department_number' in self.fields:
            options.append(orm.joinedload(model.Subdepartment.department))
        return options

    def normalize_local_object(self, subdepartment):
        data = super(SubdepartmentImporter, self).normalize_local_object(subdepartment)
        if 'department_number' in self.fields:
            dept = subdepartment.department
            data['department_number'] = dept.number if dept else None
        return data

    def update_object(self, subdepartment, data, local_data=None):
        subdepartment = super(SubdepartmentImporter, self).update_object(subdepartment, data, local_data)
        if 'department_number' in self.fields:
            dept = self.departments.get(data['department_number'])
            if not dept:
                dept = model.Department()
                dept.number = data['department_number']
                self.session.add(dept)
                self.departments[dept.number] = dept
            subdepartment.department = dept
        return subdepartment


class CategoryImporter(ToRattail):
    """
    Category data importer.
    """
    model_class = model.Category

    # set to True in order to auto-create record for "unknown" department
    auto_create_unknown_department = False

    # set to False in order to log debug instead of warning for "unknown" department
    warn_for_unknown_department = True

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'department_number',
        ]

    def setup(self):
        if 'department_number' in self.fields:
            query = self.session.query(model.Department)\
                                .filter(model.Department.number != None)
            self.departments = self.cache_model(model.Department, key='number', query=query)

    def cache_query_options(self):
        options = []
        if 'department_number' in self.fields:
            options.append(orm.joinedload(model.Category.department))
        return options

    def normalize_local_object(self, category):
        data = super(CategoryImporter, self).normalize_local_object(category)
        if 'department_number' in self.fields:
            data['department_number'] = category.department.number if category.department else None
        return data

    def get_department(self, number):
        if hasattr(self, 'departments'):
            return self.departments.get(number)
        return self.session.query(model.Department)\
                           .filter(model.Department.number == number)\
                           .first()

    def update_object(self, category, data, local_data=None):
        category = super(CategoryImporter, self).update_object(category, data, local_data)

        if 'department_number' in self.fields:
            number = data['department_number']
            if number:
                dept = self.get_department(number)
                if dept:
                    category.department = dept
                elif self.auto_create_unknown_department:
                    dept = model.Department()
                    dept.number = number
                    dept.name = "(created from import)"
                    self.session.add(dept)
                    if hasattr(self, 'departments'):
                        self.departments[dept.number] = dept
                    category.department = dept
                else:
                    logger = log.warning if self.warn_for_unknown_department else log.debug
                    logger("unknown department number '%s' for %s", number, category)
                    if category.department:
                        category.department = None
            elif category.department:
                category.department = None

        return category


class FamilyImporter(ToRattail):
    """
    Family data importer.
    """
    model_class = model.Family


class ReportCodeImporter(ToRattail):
    """
    ReportCode data importer.
    """
    model_class = model.ReportCode


class DepositLinkImporter(ToRattail):
    """
    Deposit link data importer.
    """
    model_class = model.DepositLink


class TaxImporter(ToRattail):
    """
    Tax data importer.
    """
    model_class = model.Tax


class InventoryAdjustmentReasonImporter(ToRattail):
    """
    InventoryAdjustmentReason data importer.
    """
    model_class = model.InventoryAdjustmentReason


class BrandImporter(ToRattail):
    """
    Brand data importer.
    """
    model_class = model.Brand


class ProductImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.Product`.
    """
    model_class = model.Product

    regular_price_fields = [
        'regular_price_price',
        'regular_price_multiple',
        'regular_price_pack_price',
        'regular_price_pack_multiple',
        'regular_price_type',
        'regular_price_level',
        'regular_price_starts',
        'regular_price_ends',
    ]
    sale_price_fields = [
        'sale_price_price',
        'sale_price_multiple',
        'sale_price_pack_price',
        'sale_price_pack_multiple',
        'sale_price_type',
        'sale_price_level',
        'sale_price_starts',
        'sale_price_ends',
    ]
    suggested_price_fields = [
        'suggested_price_price',
        'suggested_price_multiple',
        'suggested_price_pack_price',
        'suggested_price_pack_multiple',
        'suggested_price_type',
        'suggested_price_level',
        'suggested_price_starts',
        'suggested_price_ends',
    ]
    vendor_fields = [
        'vendor_id',
        'vendor_item_code',
        'vendor_case_cost',
        'vendor_unit_cost',
    ]

    maxlen_category_code = maxlen(model.Category.code)

    # set to True in order to auto-create record for "unknown" category
    auto_create_unknown_category = False

    # set to True in order to auto-create record for "unknown" report code
    auto_create_unknown_report_code = False

    # set to False in order to log debug instead of warning for "unknown" category
    warn_for_unknown_category = True

    # set to False in order to log debug instead of warning for "unknown" report code
    warn_for_unknown_report_code = True

    @property
    def supported_fields(self):
        return self.simple_fields + self.regular_price_fields + self.sale_price_fields + self.suggested_price_fields + self.vendor_fields + [
            'brand_name',
            'department_number',
            'subdepartment_number',
            'category_code',
            'category_number',
            'family_code',
            'report_code',
            'deposit_link_code',
            'tax_code',
        ]

    def setup(self):
        if 'brand_name' in self.fields:
            self.brands = self.cache_model(model.Brand, key='name')
        if 'department_number' in self.fields:
            query = self.session.query(model.Department)\
                                .filter(model.Department.number != None)
            self.departments = self.cache_model(model.Department, key='number', query=query)
        if 'subdepartment_number' in self.fields:
            self.subdepartments = self.cache_model(model.Subdepartment, key='number')
        if 'category_code' in self.fields:
            query = self.session.query(model.Category)\
                                .filter(model.Category.code != None)
            self.categories = self.cache_model(model.Category, key='code', query=query)
        elif 'category_number' in self.fields:
            self.categories = self.cache_model(model.Category, key='number')
        if 'family_code' in self.fields:
            self.families = self.cache_model(model.Family, key='code')
        if 'report_code' in self.fields:
            self.reportcodes = self.cache_model(model.ReportCode, key='code')
        if 'deposit_link_code' in self.fields:
            self.depositlinks = self.cache_model(model.DepositLink, key='code')
        if 'tax_code' in self.fields:
            self.taxes = self.cache_model(model.Tax, key='code')
        if 'vendor_id' in self.fields:
            self.vendors = self.cache_model(model.Vendor, key='id')

    def cache_query(self):
        query = super(ProductImporter, self).cache_query()
        if len(self.key) == 1:
            if self.key[0] == 'item_id':
                query = query.filter(model.Product.item_id != None)
            elif self.key[0] == 'upc':
                query = query.filter(model.Product.upc != None)
        return query

    def cache_query_options(self):
        options = super(ProductImporter, self).cache_query_options()
        if 'brand_name' in self.fields:
            options.append(orm.joinedload(model.Product.brand))
        if 'department_number' in self.fields:
            options.append(orm.joinedload(model.Product.department))
        if 'subdepartment_number' in self.fields:
            options.append(orm.joinedload(model.Product.subdepartment))
        if 'category_code' in self.fields or 'category_number' in self.fields:
            options.append(orm.joinedload(model.Product.category))
        if 'family_code' in self.fields:
            options.append(orm.joinedload(model.Product.family))
        if 'report_code' in self.fields:
            options.append(orm.joinedload(model.Product.report_code))
        if 'deposit_link_code' in self.fields:
            options.append(orm.joinedload(model.Product.deposit_link))
        if 'tax_code' in self.fields:
            options.append(orm.joinedload(model.Product.tax))
        joined_prices = False
        if self.fields_active(self.suggested_price_fields):
            options.append(orm.joinedload(model.Product.prices))
            options.append(orm.joinedload(model.Product.suggested_price))
            joined_prices = True
        if self.fields_active(self.regular_price_fields):
            if not joined_prices:
                options.append(orm.joinedload(model.Product.prices))
            options.append(orm.joinedload(model.Product.regular_price))
            joined_prices = True
        if self.fields_active(self.sale_price_fields):
            if not joined_prices:
                options.append(orm.joinedload(model.Product.prices))
            options.append(orm.joinedload(model.Product.current_price))
        if self.fields_active(self.vendor_fields):
            options.append(orm.joinedload(model.Product.cost))
            # options.append(orm.joinedload(model.Product.costs))
        return options

    def normalize_local_object(self, product):
        data = super(ProductImporter, self).normalize_local_object(product)

        if 'brand_name' in self.fields:
            data['brand_name'] = product.brand.name if product.brand else None
        if 'department_number' in self.fields:
            data['department_number'] = product.department.number if product.department else None
        if 'subdepartment_number' in self.fields:
            data['subdepartment_number'] = product.subdepartment.number if product.subdepartment else None
        if 'category_code' in self.fields:
            data['category_code'] = product.category.code if product.category else None
        if 'category_number' in self.fields:
            data['category_number'] = product.category.number if product.category else None
        if 'family_code' in self.fields:
            data['family_code'] = product.family.code if product.family else None
        if 'report_code' in self.fields:
            data['report_code'] = product.report_code.code if product.report_code else None
        if 'deposit_link_code' in self.fields:
            data['deposit_link_code'] = product.deposit_link.code if product.deposit_link else None
        if 'tax_code' in self.fields:
            data['tax_code'] = product.tax.code if product.tax else None

        if self.fields_active(self.suggested_price_fields):
            price = product.suggested_price
            if 'suggested_price_price' in self.fields:
                data['suggested_price_price'] = price.price if price else None
            if 'suggested_price_multiple' in self.fields:
                data['suggested_price_multiple'] = price.multiple if price else None
            if 'suggested_price_pack_price' in self.fields:
                data['suggested_price_pack_price'] = price.pack_price if price else None
            if 'suggested_price_pack_multiple' in self.fields:
                data['suggested_price_pack_multiple'] = price.pack_multiple if price else None
            if 'suggested_price_type' in self.fields:
                data['suggested_price_type'] = price.type if price else None
            if 'suggested_price_level' in self.fields:
                data['suggested_price_level'] = price.level if price else None
            if 'suggested_price_starts' in self.fields:
                data['suggested_price_starts'] = price.starts if price else None
            if 'suggested_price_ends' in self.fields:
                data['suggested_price_ends'] = price.ends if price else None

        if self.fields_active(self.regular_price_fields):
            price = product.regular_price
            if 'regular_price_price' in self.fields:
                data['regular_price_price'] = price.price if price else None
            if 'regular_price_multiple' in self.fields:
                data['regular_price_multiple'] = price.multiple if price else None
            if 'regular_price_pack_price' in self.fields:
                data['regular_price_pack_price'] = price.pack_price if price else None
            if 'regular_price_pack_multiple' in self.fields:
                data['regular_price_pack_multiple'] = price.pack_multiple if price else None
            if 'regular_price_type' in self.fields:
                data['regular_price_type'] = price.type if price else None
            if 'regular_price_level' in self.fields:
                data['regular_price_level'] = price.level if price else None
            if 'regular_price_starts' in self.fields:
                data['regular_price_starts'] = price.starts if price else None
            if 'regular_price_ends' in self.fields:
                data['regular_price_ends'] = price.ends if price else None

        if self.fields_active(self.sale_price_fields):
            price = product.current_price
            if 'sale_price_price' in self.fields:
                data['sale_price_price'] = price.price if price else None
            if 'sale_price_multiple' in self.fields:
                data['sale_price_multiple'] = price.multiple if price else None
            if 'sale_price_pack_price' in self.fields:
                data['sale_price_pack_price'] = price.pack_price if price else None
            if 'sale_price_pack_multiple' in self.fields:
                data['sale_price_pack_multiple'] = price.pack_multiple if price else None
            if 'sale_price_type' in self.fields:
                data['sale_price_type'] = price.type if price else None
            if 'sale_price_level' in self.fields:
                data['sale_price_level'] = price.level if price else None
            if 'sale_price_starts' in self.fields:
                data['sale_price_starts'] = price.starts if price else None
            if 'sale_price_ends' in self.fields:
                data['sale_price_ends'] = price.ends if price else None

        if self.fields_active(self.vendor_fields):
            cost = product.cost
            if 'vendor_id' in self.fields:
                data['vendor_id'] = cost.vendor.id if cost else None
            if 'vendor_item_code' in self.fields:
                data['vendor_item_code'] = cost.code if cost else None
            if 'vendor_case_cost' in self.fields:
                data['vendor_case_cost'] = cost.case_cost if cost else None
            if 'vendor_unit_cost' in self.fields:
                data['vendor_unit_cost'] = cost.unit_cost if cost else None

        return data

    def get_brand(self, name):
        if hasattr(self, 'brands'):
            return self.brands.get(name)
        return self.session.query(model.Brand)\
                           .filter(model.Brand.name == name)\
                           .first()

    def get_department(self, number):
        if hasattr(self, 'departments'):
            return self.departments.get(number)
        return self.session.query(model.Department)\
                           .filter(model.Department.number == number)\
                           .first()

    def get_subdepartment(self, number):
        if hasattr(self, 'subdepartments'):
            return self.subdepartments.get(number)
        return self.session.query(model.Subdepartment)\
                           .filter(model.Subdepartment.number == number)\
                           .first()

    def get_category_by_code(self, code):
        if hasattr(self, 'categories'):
            return self.categories.get(code)
        return self.session.query(model.Category)\
                           .filter(model.Category.code == code)\
                           .first()

    def get_category_by_number(self, number):
        if hasattr(self, 'categories'):
            return self.categories.get(number)
        return self.session.query(model.Category)\
                           .filter(model.Category.number == number)\
                           .first()

    def get_family(self, code):
        if hasattr(self, 'families'):
            return self.families.get(code)
        return self.session.query(model.Family)\
                           .filter(model.Family.code == code)\
                           .first()

    def get_reportcode(self, code):
        if hasattr(self, 'reportcodes'):
            return self.reportcodes.get(code)
        return self.session.query(model.ReportCode)\
                           .filter(model.ReportCode.code == code)\
                           .first()

    def get_depositlink(self, code):
        if hasattr(self, 'depositlinks'):
            return self.depositlinks.get(code)
        return self.session.query(model.DepositLink)\
                           .filter(model.DepositLink.code == code)\
                           .first()

    def get_tax(self, code):
        if hasattr(self, 'taxes'):
            return self.taxes.get(code)
        return self.session.query(model.Tax)\
                           .filter(model.Tax.code == code)\
                           .first()

    def update_object(self, product, data, local_data=None):
        product = super(ProductImporter, self).update_object(product, data, local_data)

        if 'brand_name' in self.fields:
            name = data['brand_name']
            if name:
                brand = self.get_brand(name)
                if not brand:
                    brand = model.Brand()
                    brand.name = name
                    self.session.add(brand)
                    if hasattr(self, 'brands'):
                        self.brands[brand.name] = brand
                product.brand = brand
            elif product.brand:
                product.brand = None

        if 'department_number' in self.fields:
            number = data['department_number']
            if number:
                dept = self.get_department(number)
                if not dept:
                    dept = model.Department()
                    dept.number = number
                    dept.name = "(auto-created)"
                    self.session.add(dept)
                    if hasattr(self, 'departments'):
                        self.departments[dept.number] = dept
                product.department = dept
            elif product.department:
                product.department = None

        if 'subdepartment_number' in self.fields:
            number = data['subdepartment_number']
            if number:
                sub = self.get_subdepartment(number)
                if not sub:
                    sub = model.Subdepartment()
                    sub.number = number
                    sub.name = "(auto-created)"
                    self.session.add(sub)
                    if hasattr(self, 'subdepartments'):
                        self.subdepartments[number] = sub
                product.subdepartment = sub
            elif product.subdepartment:
                product.subdepartment = None

        if 'category_code' in self.fields:
            code = data['category_code']
            if code:
                if len(code) > self.maxlen_category_code:
                    log.warning("category code length ({}) exceeds max allowed ({}): {}".format(
                        len(code), self.maxlen_category_code, code))
                    code = code[:self.maxlen_category_code]

                category = self.get_category_by_code(code)
                if category:
                    product.category = category
                elif self.auto_create_unknown_category:
                    category = model.Category()
                    category.code = code
                    try:
                        category.number = int(code)
                    except ValueError:
                        pass
                    self.session.add(category)
                    if hasattr(self, 'categories'):
                        self.categories[code] = category
                    product.category = category
                else:
                    logger = log.warning if self.warn_for_unknown_category else log.debug
                    logger("unknown category code '%s' for %s", code, product)
                    if product.category:
                        product.category = None

            elif product.category:
                product.category = None

        elif 'category_number' in self.fields:
            number = data['category_number']
            if number:
                category = self.get_category_by_number(number)
                if category:
                    product.category = category
                elif self.auto_create_unknown_category:
                    category = model.Category()
                    category.number = number
                    category.code = six.text_type(number)
                    category.name = "(auto-created)"
                    self.session.add(category)
                    if hasattr(self, 'categories'):
                        self.categories[number] = category
                    product.category = category
                else:
                    logger = log.warning if self.warn_for_unknown_category else log.debug
                    logger("unknown category number '%s' for %s", number, product)
                    if product.category:
                        product.category = None
            elif product.category:
                product.category = None

        if 'family_code' in self.fields:
            code = data['family_code']
            if code:
                family = self.get_family(code)
                if not family:
                    family = model.Family()
                    family.code = code
                    family.name = "(auto-created)"
                    self.session.add(family)
                    if hasattr(self, 'families'):
                        self.families[family.code] = family
                product.family = family
            elif product.family:
                product.family = None

        if 'report_code' in self.fields:
            code = data['report_code']
            if code:
                rc = self.get_reportcode(code)
                if rc:
                    product.report_code = rc
                elif self.auto_create_unknown_report_code:
                    rc = model.ReportCode()
                    rc.code = code
                    rc.name = "(no name)"
                    self.session.add(rc)
                    if hasattr(self, 'reportcodes'):
                        self.reportcodes[rc.code] = rc
                    product.report_code = rc
                else:
                    logger = log.warning if self.warn_for_unknown_report_code else log.debug
                    logger("unknown report code '%s' for %s", code, product)
                    if product.report_code:
                        product.report_code = None
            elif product.report_code:
                product.report_code = None

        if 'deposit_link_code' in self.fields:
            code = data['deposit_link_code']
            if code:
                link = self.get_depositlink(code)
                if not link:
                    link = model.DepositLink()
                    link.code = code
                    link.description = "(auto-created)"
                    self.session.add(link)
                    if hasattr(self, 'depositlinks'):
                        self.depositlinks[link.code] = link
                product.deposit_link = link
            elif product.deposit_link:
                product.deposit_link = None

        if 'tax_code' in self.fields:
            code = data['tax_code']
            if code:
                tax = self.get_tax(code)
                if not tax:
                    tax = model.Tax()
                    tax.code = code
                    tax.description = code
                    tax.rate = 0
                    self.session.add(tax)
                    if hasattr(self, 'taxes'):
                        self.taxes[tax.code] = tax
                product.tax = tax
            elif product.tax:
                product.tax = None

        create = False
        delete = False
        if self.fields_active(self.suggested_price_fields):
            delete = True
            create = any([data.get(f) is not None for f in self.suggested_price_fields])
        if create:
            price = product.suggested_price
            if not price:
                price = model.ProductPrice()
                product.prices.append(price)
                product.suggested_price = price
            if 'suggested_price_price' in self.fields:
                price.price = data['suggested_price_price']
            if 'suggested_price_multiple' in self.fields:
                price.multiple = data['suggested_price_multiple']
            if 'suggested_price_pack_price' in self.fields:
                price.pack_price = data['suggested_price_pack_price']
            if 'suggested_price_pack_multiple' in self.fields:
                price.pack_multiple = data['suggested_price_pack_multiple']
            if 'suggested_price_type' in self.fields:
                price.type = data['suggested_price_type']
            if 'suggested_price_level' in self.fields:
                price.level = data['suggested_price_level']
            if 'suggested_price_starts' in self.fields:
                price.starts = data['suggested_price_starts']
            if 'suggested_price_ends' in self.fields:
                price.ends = data['suggested_price_ends']
        elif delete and product.suggested_price:
            product.suggested_price = None

        create = False
        delete = False
        if self.fields_active(self.regular_price_fields):
            delete = True
            create = any([data.get(f) is not None for f in self.regular_price_fields])
        if create:
            price = product.regular_price
            if not price:
                price = model.ProductPrice()
                product.prices.append(price)
                product.regular_price = price
            if 'regular_price_price' in self.fields:
                price.price = data['regular_price_price']
            if 'regular_price_multiple' in self.fields:
                price.multiple = data['regular_price_multiple']
            if 'regular_price_pack_price' in self.fields:
                price.pack_price = data['regular_price_pack_price']
            if 'regular_price_pack_multiple' in self.fields:
                price.pack_multiple = data['regular_price_pack_multiple']
            if 'regular_price_type' in self.fields:
                price.type = data['regular_price_type']
            if 'regular_price_level' in self.fields:
                price.level = data['regular_price_level']
            if 'regular_price_starts' in self.fields:
                price.starts = data['regular_price_starts']
            if 'regular_price_ends' in self.fields:
                price.ends = data['regular_price_ends']
        elif delete and product.regular_price:
            product.regular_price = None

        create = False
        delete = False
        if self.fields_active(self.sale_price_fields):
            delete = True
            create = any([data.get(f) is not None for f in self.sale_price_fields])
        if create:
            price = product.current_price
            if not price:
                price = model.ProductPrice()
                product.prices.append(price)
                product.current_price = price
            if 'sale_price_price' in self.fields:
                price.price = data['sale_price_price']
            if 'sale_price_multiple' in self.fields:
                price.multiple = data['sale_price_multiple']
            if 'sale_price_pack_price' in self.fields:
                price.pack_price = data['sale_price_pack_price']
            if 'sale_price_pack_multiple' in self.fields:
                price.pack_multiple = data['sale_price_pack_multiple']
            if 'sale_price_type' in self.fields:
                price.type = data['sale_price_type']
            if 'sale_price_level' in self.fields:
                price.level = data['sale_price_level']
            if 'sale_price_starts' in self.fields:
                price.starts = data['sale_price_starts']
            if 'sale_price_ends' in self.fields:
                price.ends = data['sale_price_ends']
        elif delete and product.current_price:
            product.current_price = None

        if 'vendor_id' in self.fields:
            vendor_id = data['vendor_id']
            if vendor_id:
                vendor = self.vendors.get(vendor_id)
                if not vendor:
                    vendor = model.Vendor()
                    vendor.id = vendor_id
                    self.session.add(vendor)
                    self.vendors[vendor_id] = vendor
                if product.cost:
                    if product.cost.vendor is not vendor:
                        cost = product.cost_for_vendor(vendor)
                        if not cost:
                            cost = model.ProductCost()
                            cost.vendor = vendor
                        product.costs.insert(0, cost)
                else:
                    cost = model.ProductCost()
                    cost.vendor = vendor
                    with self.session.no_autoflush:
                        product.costs.append(cost)
                    # TODO: This seems heavy-handed, but also seems necessary
                    # to populate the `Product.cost` relationship...
                    self.session.add(product)
                    self.session.flush()
                    self.session.refresh(product)
            else:
                if product.cost:
                    del product.costs[:]

        if 'vendor_item_code' in self.fields:
            code = data['vendor_item_code']
            if data.get('vendor_id'):
                if product.cost:
                    product.cost.code = code
                else:
                    log.warning("product has no cost, so can't set vendor_item_code: {}".format(product))

        if 'vendor_case_cost' in self.fields:
            cost = data['vendor_case_cost']
            if data.get('vendor_id'):
                if product.cost:
                    product.cost.case_cost = cost
                else:
                    log.warning("product has no cost, so can't set vendor_case_cost: {}".format(product))

        if 'vendor_unit_cost' in self.fields:
            cost = data['vendor_unit_cost']
            if data.get('vendor_id'):
                if product.cost:
                    product.cost.unit_cost = cost
                else:
                    log.warning("product has no cost, so can't set vendor_case_cost: {}".format(product))

        return product


class ProductImageImporter(BatchImporter, ToRattail):
    """
    Importer for product images data.  Note that this uses the "batch" approach
    because fetching all data up front is not performant when the host/local
    systems are on different machines etc.
    """
    model_class = model.ProductImage


class ProductCodeImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.ProductCode`.
    """
    model_class = model.ProductCode

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'product_upc',
            'primary',
        ]

    def setup(self):
        if 'product_upc' in self.fields:
            self.products = self.cache_model(model.Product, key='upc')

    def cache_query_options(self):
        options = []
        if 'product_upc' in self.fields:
            options.append(orm.joinedload(model.ProductCode.product))
        return options

    def get_single_local_object(self, key):
        """
        Fetch a single ``ProductCode`` object from local Rattail, taking
        complex key fields (namely ``product_upc``) into account.
        """
        query = self.session.query(model.ProductCode)
        for i, k in enumerate(self.key):
            if k != 'product_upc':
                query = query.filter(getattr(self.model_class, k) == key[i])
        try:
            i = self.key.index('product_upc')
        except ValueError:
            pass
        else:
            query = query.join(model.Product).filter(model.Product.upc == key[i])
        try:
            return query.one()
        except NoResultFound:
            pass

    def normalize_local_object(self, code):
        data = super(ProductCodeImporter, self).normalize_local_object(code)
        if 'product_upc' in self.fields:
            data['product_upc'] = code.product.upc
        if 'primary' in self.fields:
            data['primary'] = code.ordinal == 1
        return data

    def get_product(self, upc):
        if hasattr(self, 'products'):
            return self.products.get(upc)
        return self.session.query(model.Product)\
                           .filter(model.Product.upc == upc)\
                           .first()

    def new_object(self, key):
        code = super(ProductCodeImporter, self).new_object(key)
        if 'product_upc' in self.key:
            i = list(self.key).index('product_upc')
            product = self.get_product(key[i])
            if not product:
                log.error("product not found for key: {}".format(key))
                return
            product._codes.append(code)
        return code

    def update_object(self, code, data, local_data=None):
        code = super(ProductCodeImporter, self).update_object(code, data, local_data)

        if 'product_upc' in self.fields and 'product_uuid' not in self.fields:
            upc = data['product_upc']
            assert upc, "Source data has no product_upc value: {}".format(repr(data))
            product = self.get_product(upc)
            if not product:
                product = model.Product()
                product.upc = upc
                self.session.add(product)
                if hasattr(self, 'products'):
                    self.products[product.upc] = product
                product._codes.append(code)
            elif code not in product._codes:
                product._codes.append(code)

        if 'primary' in self.fields:
            if data['primary'] and code.ordinal != 1:
                product = code.product
                product._codes.remove(code)
                product._codes.insert(0, code)
                product._codes.reorder()
            elif data['primary'] is False and code.ordinal == 1:
                product = code.product
                if len(product._codes) > 1:
                    product._codes.remove(code)
                    product._codes.append(code)
                    product._codes.reorder()

        return code


class ProductCostImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.ProductCost`.
    """
    model_class = model.ProductCost

    product_key_fields = [
        'product_upc',
        'product_item_id',
    ]

    @property
    def supported_fields(self):
        return self.simple_fields + self.product_key_fields + [
            'vendor_id',
            'preferred',
        ]

    def setup(self):

        # note that only one product key field should be supported
        if 'product_upc' in self.fields:
            query = self.session.query(model.Product)\
                                .filter(model.Product.upc != None)
            self.products = self.cache_model(model.Product, query=query, key='upc')
        elif 'product_item_id' in self.fields:
            query = self.session.query(model.Product)\
                                .filter(model.Product.item_id != None)
            self.products = self.cache_model(model.Product, query=query, key='item_id')

        if 'vendor_id' in self.fields:
            self.vendors = self.cache_model(model.Vendor, key='id')

    def cache_query_options(self):
        options = []
        if self.fields_active(self.product_key_fields):
            options.append(orm.joinedload(model.ProductCost.product))
        if 'vendor_id' in self.fields:
            options.append(orm.joinedload(model.ProductCost.vendor))
        return options

    def get_single_local_object(self, key):
        """
        Fetch a single ``ProductCost`` object from local Rattail, taking
        complex key fields (e.g. ``product_upc``, ``vendor_id``) into account.
        """
        query = self.session.query(model.ProductCost)
        for i, k in enumerate(self.key):
            if k not in ('product_upc', 'product_item_id', 'vendor_id'):
                query = query.filter(getattr(self.model_class, k) == key[i])

        try:
            i = self.key.index('product_upc')
        except ValueError:
            pass
        else:
            query = query.join(model.Product).filter(model.Product.upc == key[i])

        try:
            i = self.key.index('product_item_id')
        except ValueError:
            pass
        else:
            query = query.join(model.Product).filter(model.Product.item_id == key[i])

        try:
            i = self.key.index('vendor_id')
        except ValueError:
            pass
        else:
            query = query.join(model.Vendor).filter(model.Vendor.id == key[i])

        try:
            return query.one()
        except NoResultFound:
            pass

    def normalize_local_object(self, cost):
        data = super(ProductCostImporter, self).normalize_local_object(cost)
        if 'product_upc' in self.fields:
            data['product_upc'] = cost.product.upc
        if 'product_item_id' in self.fields:
            data['product_item_id'] = cost.product.item_id
        if 'vendor_id' in self.fields:
            data['vendor_id'] = cost.vendor.id
        if 'preferred' in self.fields:
            data['preferred'] = cost.preference == 1
        return data
        
    def get_product(self, upc):
        if hasattr(self, 'products'):
            return self.products.get(upc)
        return self.session.query(model.Product)\
                           .filter(model.Product.upc == upc)\
                           .first()

    def get_product_by_item_id(self, item_id):
        if hasattr(self, 'products'):
            return self.products.get(item_id)
        return self.session.query(model.Product)\
                           .filter(model.Product.item_id == item_id)\
                           .first()

    def get_vendor(self, vendor_id):
        if hasattr(self, 'vendors'):
            return self.vendors.get(vendor_id)
        return self.session.query(model.Vendor)\
                           .filter(model.Vendor.id == vendor_id)\
                           .first()

    def update_object(self, cost, data, local_data=None):
        cost = super(ProductCostImporter, self).update_object(cost, data, local_data)

        if 'vendor_id' in self.fields and 'vendor_uuid' not in self.fields:
            vendor_id = data['vendor_id']
            assert vendor_id, "Source data has no vendor_id value: {}".format(repr(data))
            vendor = self.get_vendor(vendor_id)
            if not vendor:
                vendor = model.Vendor()
                vendor.id = vendor_id
                self.session.add(vendor)
                self.session.flush()
                if hasattr(self, 'vendors'):
                    self.vendors[vendor.id] = vendor
            cost.vendor = vendor

        if 'product_upc' in self.fields and 'product_uuid' not in self.fields:
            upc = data['product_upc']
            assert upc, "Source data has no product_upc value: {}".format(repr(data))
            product = self.get_product(upc)
            if not product:
                product = model.Product()
                product.upc = upc
                self.session.add(product)
                if hasattr(self, 'products'):
                    self.products[product.upc] = product
            if not cost.product:
                product.costs.append(cost)
            elif cost.product is not product:
                log.warning("duplicate products detected for UPC {}".format(upc.pretty()))

        if 'product_item_id' in self.fields and 'product_uuid' not in self.fields:
            item_id = data['product_item_id']
            if not item_id:
                raise ValueError("Source data has no product_item_id value: {}".format(data))
            product = self.get_product_by_item_id(item_id)
            if not product:
                product = model.Product()
                product.item_id = item_id
                self.session.add(product)
                if hasattr(self, 'products'):
                    self.products[product.item_id] = product
            if not cost.product:
                product.costs.append(cost)
            elif cost.product is not product:
                log.warning("duplicate products detected for item_id: %s", item_id)

        if 'preferred' in self.fields:
            product = cost.product or self.session.query(model.Product).get(cost.product_uuid)
            if data['preferred']:
                if cost in product.costs:
                    if cost.preference != 1:
                        product.costs.remove(cost)
                        product.costs.insert(0, cost)
                elif product.costs:
                    product.costs.insert(0, cost)
                else:
                    product.costs.append(cost)
            else: # not preferred
                if cost in product.costs:
                    if cost.preference == 1:
                        if len(product.costs) > 1:
                            product.costs.remove(cost)
                            product.costs.append(cost)
                            product.costs.reorder()
                        else:
                            log.warning("cannot un-prefer cost, as product has only the one: {}".format(cost))
                else:
                    if not product.costs:
                        log.warning("new cost will be preferred, as product has only the one: {}".format(self.get_key(data)))
                    product.costs.append(cost)
                    product.costs.reorder()

        return cost


class ProductPriceImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.ProductPrice`.
    """
    model_class = model.ProductPrice

    product_reference_fields = [
        'product_suggested_price',
        'product_regular_price',
        'product_current_price',
    ]

    @property
    def supported_fields(self):
        return self.simple_fields + self.product_reference_fields

    def cache_query_options(self):
        options = []
        if self.fields_active(self.product_reference_fields):
            options.append(orm.joinedload(model.ProductPrice.product))
        return options

    def normalize_local_object(self, price):
        data = super(ProductPriceImporter, self).normalize_local_object(price)

        if self.fields_active(self.product_reference_fields):
            product = price.product
            if 'product_suggested_price' in self.fields:
                data['product_suggested_price'] = bool(product.suggested_price is price)
            if 'product_regular_price' in self.fields:
                data['product_regular_price'] = bool(product.regular_price is price)
            if 'product_current_price' in self.fields:
                data['product_current_price'] = bool(product.current_price is price)

        return data

    def update_object(self, price, data, local_data=None):
        price = super(ProductPriceImporter, self).update_object(price, data, local_data)

        if self.fields_active(self.product_reference_fields):
            if not price.product:
                self.session.add(price)
                self.session.flush()
                self.session.refresh(price)
            product = price.product
            assert product
            assert price in product.prices

            if 'product_suggested_price' in self.fields:
                if data['product_suggested_price']:
                    if product.suggested_price is not price:
                        product.suggested_price = price
                else:
                    if product.suggested_price is price:
                        product.suggested_price = None

            if 'product_regular_price' in self.fields:
                if data['product_regular_price']:
                    if product.regular_price is not price:
                        product.regular_price = price
                else:
                    if product.regular_price is price:
                        product.regular_price = None

            if 'product_current_price' in self.fields:
                if data['product_current_price']:
                    if product.current_price is not price:
                        product.current_price = price
                else:
                    if product.current_price is price:
                        product.current_price = None

        return price


class ProductStoreInfoImporter(ToRattail):
    """
    Data importer for :class:`rattail.db.model.ProductStoreInfo`.
    """
    model_class = model.ProductStoreInfo


class ProductVolatileImporter(ToRattail):
    """
    Data importer for :class:`~rattail.db.model.products.ProductVolatile`.
    """
    model_class = model.ProductVolatile


class LabelProfileImporter(ToRattail):
    """
    Importer for LabelProfile data
    """
    model_class = model.LabelProfile

    def cache_query(self):
        query = super(LabelProfileImporter, self).cache_query()

        if not self.config.getbool('rattail', 'labels.sync_all_profiles', default=False):
            # only fetch labels from host which are marked as "sync me"
            query = query .filter(self.model_class.sync_me == True)

        return query


class CustomerOrderImporter(ToRattail):
    """
    Importer for CustomerOrder data
    """
    model_class = model.CustomerOrder


class CustomerOrderItemImporter(ToRattail):
    """
    Importer for CustomerOrderItem data
    """
    model_class = model.CustomerOrderItem


class CustomerOrderItemEventImporter(ToRattail):
    """
    Importer for CustomerOrderItemEvent data
    """
    model_class = model.CustomerOrderItemEvent

    def setup(self):
        super(CustomerOrderItemEventImporter, self).setup()

        self.start_date = self.args.start_date
        if self.start_date:
            midnight = datetime.datetime.combine(self.start_date, datetime.time(0))
            self.start_time = localtime(self.config, midnight)

        self.end_date = self.args.end_date
        if self.end_date:
            midnight = datetime.datetime.combine(self.end_date + datetime.timedelta(days=1), datetime.time(0))
            self.end_time = localtime(self.config, midnight)

    def cache_query(self):
        query = self.session.query(model.CustomerOrderItemEvent)
        if self.start_date:
            query = query.filter(model.CustomerOrderItemEvent.occurred >= make_utc(self.start_time))
        if self.end_date:
            query = query.filter(model.CustomerOrderItemEvent.occurred < make_utc(self.end_time))
        return query
