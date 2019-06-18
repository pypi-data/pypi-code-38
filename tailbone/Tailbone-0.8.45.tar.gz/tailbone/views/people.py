# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Person Views
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model, api

import colander
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from webhelpers2.html import HTML, tags

from tailbone import forms, grids
from tailbone.views import MasterView, AutocompleteView


class PeopleView(MasterView):
    """
    Master view for the Person class.
    """
    model_class = model.Person
    model_title_plural = "People"
    route_prefix = 'people'
    has_versions = True
    supports_mobile = True
    manage_notes_from_profile_view = False

    grid_columns = [
        'display_name',
        'first_name',
        'last_name',
        'phone',
        'email',
    ]

    form_fields = [
        'first_name',
        'middle_name',
        'last_name',
        'display_name',
        'phone',
        'email',
        'address',
        'employee',
        'customers',
        'users',
    ]

    mobile_form_fields = [
        'first_name',
        'middle_name',
        'last_name',
        'display_name',
        'phone',
        'email',
        'address',
        'employee',
        'customers',
        'users',
    ]

    def configure_grid(self, g):
        super(PeopleView, self).configure_grid(g)

        g.joiners['email'] = lambda q: q.outerjoin(model.PersonEmailAddress, sa.and_(
            model.PersonEmailAddress.parent_uuid == model.Person.uuid,
            model.PersonEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.PersonPhoneNumber, sa.and_(
            model.PersonPhoneNumber.parent_uuid == model.Person.uuid,
            model.PersonPhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.PersonEmailAddress.address)
        g.set_filter('phone', model.PersonPhoneNumber.number,
                     factory=grids.filters.AlchemyPhoneNumberFilter)

        g.joiners['customer_id'] = lambda q: q.outerjoin(model.CustomerPerson).outerjoin(model.Customer)
        g.filters['customer_id'] = g.make_filter('customer_id', model.Customer.id)

        g.filters['first_name'].default_active = True
        g.filters['first_name'].default_verb = 'contains'

        g.filters['last_name'].default_active = True
        g.filters['last_name'].default_verb = 'contains'

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.PersonEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.PersonPhoneNumber.number, d)())

        g.set_sort_defaults('display_name')

        g.set_label('display_name', "Full Name")
        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")
        g.set_label('customer_id', "Customer ID")

        g.set_link('display_name')
        g.set_link('first_name')
        g.set_link('last_name')

    def get_instance(self):
        # TODO: I don't recall why this fallback check for a vendor contact
        # exists here, but leaving it intact for now.
        key = self.request.matchdict['uuid']
        instance = self.Session.query(model.Person).get(key)
        if instance:
            return instance
        instance = self.Session.query(model.VendorContact).get(key)
        if instance:
            return instance.person
        raise HTTPNotFound

    def editable_instance(self, person):
        if self.rattail_config.demo():
            return not bool(person.user and person.user.username == 'chuck')
        return True

    def deletable_instance(self, person):
        if self.rattail_config.demo():
            return not bool(person.user and person.user.username == 'chuck')
        return True

    def configure_common_form(self, f):
        super(PeopleView, self).configure_common_form(f)

        f.set_label('display_name', "Full Name")

        f.set_readonly('phone')
        f.set_label('phone', "Phone Number")

        f.set_readonly('email')
        f.set_label('email', "Email Address")

        f.set_readonly('address')
        f.set_label('address', "Mailing Address")

        # employee
        if self.creating:
            f.remove_field('employee')
        else:
            f.set_readonly('employee')
            f.set_renderer('employee', self.render_employee)

        # customers
        if self.creating:
            f.remove_field('customers')
        else:
            f.set_readonly('customers')
            f.set_renderer('customers', self.render_customers)

        # users
        if self.creating:
            f.remove_field('users')
        else:
            f.set_readonly('users')
            f.set_renderer('users', self.render_users)

    def render_employee(self, person, field):
        employee = person.employee
        if not employee:
            return ""
        text = six.text_type(employee)
        url = self.request.route_url('employees.view', uuid=employee.uuid)
        return tags.link_to(text, url)

    def render_customers(self, person, field):
        customers = person._customers
        if not customers:
            return ""
        items = []
        for customer in customers:
            customer = customer.customer
            text = six.text_type(customer)
            if customer.id:
                text = "({}) {}".format(customer.id, text)
            elif customer.number:
                text = "({}) {}".format(customer.number, text)
            route = '{}customers.view'.format('mobile.' if self.mobile else '')
            url = self.request.route_url(route, uuid=customer.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def render_users(self, person, field):
        use_buefy = self.get_use_buefy()
        users = person.users
        items = []
        for user in users:
            text = user.username
            url = self.request.route_url('users.view', uuid=user.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        if items:
            return HTML.tag('ul', c=items)
        elif self.request.has_perm('users.create'):
            if use_buefy:
                return HTML.tag('button', type='button', class_='button is-primary',
                                id='make-user', c="Make User")
            else:
                return HTML.tag('button', type='button', id='make-user', c="Make User")
        else:
            return ""

    def get_version_child_classes(self):
        return [
            (model.PersonPhoneNumber, 'parent_uuid'),
            (model.PersonEmailAddress, 'parent_uuid'),
            (model.PersonMailingAddress, 'parent_uuid'),
            (model.Employee, 'person_uuid'),
            (model.CustomerPerson, 'person_uuid'),
            (model.VendorContact, 'person_uuid'),
        ]

    def view_profile(self):
        """
        View which exposes the "full profile" for a given person, i.e. all
        related customer, employee, user info etc.
        """
        self.viewing = True
        person = self.get_instance()
        employee = person.employee
        context = {
            'person': person,
            'instance': person,
            'instance_title': self.get_instance_title(person),
            'employee': employee,
            'employee_history': employee.get_current_history() if employee else None,
        }
        use_buefy = self.get_use_buefy()
        template = 'view_profile_buefy' if use_buefy else 'view_profile'
        return self.render_to_response(template, context)

    def make_note_form(self, mode, person):
        schema = NoteSchema().bind(session=self.Session(),
                                   person_uuid=person.uuid)
        if mode == 'create':
            del schema['uuid']
        form = forms.Form(schema=schema, request=self.request)
        return form

    def profile_add_note(self):
        person = self.get_instance()
        form = self.make_note_form('create', person)
        if form.validate(newstyle=True):
            note = self.create_note(person, form)
            self.Session.flush()
            return self.profile_add_note_success(note)
        else:
            return self.profile_add_note_failure(person, form)

    def create_note(self, person, form):
        note = model.PersonNote()
        note.type = form.validated['note_type']
        note.subject = form.validated['note_subject']
        note.text = form.validated['note_text']
        note.created_by = self.request.user
        person.notes.append(note)
        return note

    def profile_add_note_success(self, note):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_add_note_failure(self, person, form):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_edit_note(self):
        person = self.get_instance()
        form = self.make_note_form('edit', person)
        if form.validate(newstyle=True):
            note = self.update_note(person, form)
            self.Session.flush()
            return self.profile_edit_note_success(note)
        else:
            return self.profile_edit_note_failure(person, form)

    def update_note(self, person, form):
        note = self.Session.query(model.PersonNote).get(form.validated['uuid'])
        note.subject = form.validated['note_subject']
        note.text = form.validated['note_text']
        return note

    def profile_edit_note_success(self, note):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_edit_note_failure(self, person, form):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_delete_note(self):
        person = self.get_instance()
        form = self.make_note_form('delete', person)
        if form.validate(newstyle=True):
            self.delete_note(person, form)
            self.Session.flush()
            return self.profile_delete_note_success(person)
        else:
            return self.profile_delete_note_failure(person, form)

    def delete_note(self, person, form):
        note = self.Session.query(model.PersonNote).get(form.validated['uuid'])
        self.Session.delete(note)

    def profile_delete_note_success(self, person):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_delete_note_failure(self, person, form):
        return self.redirect(self.get_action_url('view_profile', person))

    def make_user(self):
        uuid = self.request.POST['person_uuid']
        person = self.Session.query(model.Person).get(uuid)
        if not person:
            return self.notfound()
        if person.users:
            raise RuntimeError("person {} already has {} user accounts: ".format(
                person.uuid, len(person.users), person))
        user = model.User()
        user.username = api.make_username(person)
        user.person = person
        user.active = False
        self.Session.add(user)
        self.Session.flush()
        self.request.session.flash("User has been created: {}".format(user.username))
        return self.redirect(self.request.route_url('users.view', uuid=user.uuid))

    @classmethod
    def defaults(cls, config):
        cls._people_defaults(config)
        cls._defaults(config)

    @classmethod
    def _people_defaults(cls, config):
        permission_prefix = cls.get_permission_prefix()
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # view profile
        config.add_tailbone_permission(permission_prefix, '{}.view_profile'.format(permission_prefix),
                                       "View full \"profile\" for {}".format(model_title))
        config.add_route('{}.view_profile'.format(route_prefix), '{}/{{{}}}/profile'.format(url_prefix, model_key),
                         request_method='GET')
        config.add_view(cls, attr='view_profile', route_name='{}.view_profile'.format(route_prefix),
                        permission='{}.view_profile'.format(permission_prefix))

        # manage notes from profile view
        if cls.manage_notes_from_profile_view:

            # add note
            config.add_tailbone_permission(permission_prefix, '{}.profile_add_note'.format(permission_prefix),
                                           "Add new {} note from profile view".format(model_title))
            config.add_route('{}.profile_add_note'.format(route_prefix), '{}/{{{}}}/profile/new-note'.format(url_prefix, model_key),
                             request_method='POST')
            config.add_view(cls, attr='profile_add_note', route_name='{}.profile_add_note'.format(route_prefix),
                            permission='{}.profile_add_note'.format(permission_prefix))

            # edit note
            config.add_tailbone_permission(permission_prefix, '{}.profile_edit_note'.format(permission_prefix),
                                           "Edit existing {} note from profile view".format(model_title))
            config.add_route('{}.profile_edit_note'.format(route_prefix), '{}/{{{}}}/profile/edit-note'.format(url_prefix, model_key),
                             request_method='POST')
            config.add_view(cls, attr='profile_edit_note', route_name='{}.profile_edit_note'.format(route_prefix),
                            permission='{}.profile_edit_note'.format(permission_prefix))

            # delete note
            config.add_tailbone_permission(permission_prefix, '{}.profile_delete_note'.format(permission_prefix),
                                           "Delete existing {} note from profile view".format(model_title))
            config.add_route('{}.profile_delete_note'.format(route_prefix), '{}/{{{}}}/profile/delete-note'.format(url_prefix, model_key),
                             request_method='POST')
            config.add_view(cls, attr='profile_delete_note', route_name='{}.profile_delete_note'.format(route_prefix),
                            permission='{}.profile_delete_note'.format(permission_prefix))

        # make user for person
        config.add_route('{}.make_user'.format(route_prefix), '{}/make-user'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='make_user', route_name='{}.make_user'.format(route_prefix),
                        permission='users.create')


class PeopleAutocomplete(AutocompleteView):

    mapped_class = model.Person
    fieldname = 'display_name'


class PeopleEmployeesAutocomplete(PeopleAutocomplete):
    """
    Autocomplete view for the Person model, but restricted to return only
    results for people who are employees.
    """

    def filter_query(self, q):
        return q.join(model.Employee)


class PersonNoteView(MasterView):
    """
    Master view for the PersonNote class.
    """
    model_class = model.PersonNote
    route_prefix = 'person_notes'
    url_prefix = '/people/notes'
    has_versions = True

    grid_columns = [
        'person',
        'type',
        'subject',
        'created',
        'created_by',
    ]

    form_fields = [
        'person',
        'type',
        'subject',
        'text',
        'created',
        'created_by',
    ]

    def get_instance_title(self, note):
        return note.subject or "(no subject)"

    def configure_grid(self, g):
        super(PersonNoteView, self).configure_grid(g)

        # person
        g.set_joiner('person', lambda q: q.join(model.Person,
                                                model.Person.uuid == model.PersonNote.parent_uuid))
        g.set_sorter('person', model.Person.display_name)
        g.set_filter('person', model.Person.display_name, label="Person Name")

        # created_by
        CreatorPerson = orm.aliased(model.Person)
        g.set_joiner('created_by', lambda q: q.join(model.User).outerjoin(CreatorPerson,
                                                                          CreatorPerson.uuid == model.User.person_uuid))
        g.set_sorter('created_by', CreatorPerson.display_name)

        g.set_sort_defaults('created', 'desc')

        g.set_link('person')
        g.set_link('subject')
        g.set_link('created')

    def configure_form(self, f):
        super(PersonNoteView, self).configure_form(f)

        # person
        f.set_readonly('person')
        f.set_renderer('person', self.render_person)

        # created
        f.set_readonly('created')

        # created_by
        f.set_readonly('created_by')
        f.set_renderer('created_by', self.render_user)


@colander.deferred
def valid_note_uuid(node, kw):
    session = kw['session']
    person_uuid = kw['person_uuid']
    def validate(node, value):
        note = session.query(model.PersonNote).get(value)
        if not note:
            raise colander.Invalid(node, "Note not found")
        if note.person.uuid != person_uuid:
            raise colander.Invalid(node, "Note is for the wrong person")
        return note.uuid
    return validate


class NoteSchema(colander.Schema):

    uuid = colander.SchemaNode(colander.String(),
                               validator=valid_note_uuid)

    note_type = colander.SchemaNode(colander.String())

    note_subject = colander.SchemaNode(colander.String(), missing='')

    note_text = colander.SchemaNode(colander.String(), missing='')


def includeme(config):

    # autocomplete
    config.add_route('people.autocomplete', '/people/autocomplete')
    config.add_view(PeopleAutocomplete, route_name='people.autocomplete',
                    renderer='json', permission='people.list')
    config.add_route('people.autocomplete.employees', '/people/autocomplete/employees')
    config.add_view(PeopleEmployeesAutocomplete, route_name='people.autocomplete.employees',
                    renderer='json', permission='people.list')

    PeopleView.defaults(config)
    PersonNoteView.defaults(config)
