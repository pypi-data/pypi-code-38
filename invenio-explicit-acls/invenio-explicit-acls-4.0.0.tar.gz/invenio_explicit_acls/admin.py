#
# Copyright (c) 2019 UCT Prague.
# 
# admin.py is part of Invenio Explicit ACLs 
# (see https://github.com/oarepo/invenio-explicit-acls).
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Admin interface."""
from __future__ import absolute_import, print_function

import traceback

from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from flask_admin.model import InlineFormAdmin
from flask_login import current_user
from flask_wtf import FlaskForm
from invenio_jsonschemas import current_jsonschemas
from invenio_records import Record
from invenio_search import current_search_client
from wtforms import SelectField
from wtforms.validators import StopValidation

from invenio_explicit_acls.acls import ElasticsearchACL, IdACL
from invenio_explicit_acls.acls.default_acls import DefaultACL
from invenio_explicit_acls.acls.propertyvalue_acls import BoolOperation, \
    MatchOperation, PropertyValue, PropertyValueACL
from invenio_explicit_acls.actors import RoleActor, SystemRoleActor, UserActor
from invenio_explicit_acls.proxies import current_explicit_acls


def _(x):
    """Identity function for string extraction."""
    return x


class OriginatorMixin(object):
    """Mixin that sets model's originator property to the current user."""

    def on_model_change(self, form, model, is_created):
        """Sets the originator property."""
        model.originator = current_user


def schemas_choices():
    """Returns sorted known schemas."""
    return list(sorted(current_jsonschemas.schemas.keys()))


class FieldValidatorMixin(object):
    """Mixin that adds support for validate_{propertyname} methods."""

    def validate_form(self, form):
        """Overwrites validate_form and for each model property runs validation method if exists."""
        if not super().validate_form(form):
            return False

        errors = False
        for fld in form._fields:
            method = getattr(self, f'validate_{fld}', None)
            if not method:
                continue
            try:
                method(form, getattr(form, fld))
            except StopValidation as e:
                getattr(form, fld).errors.append(str(e))
                errors = True

        return not errors


class ACLModelViewMixin(FieldValidatorMixin, OriginatorMixin):
    """A mixin that triggers extra processing of ACLs."""

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    def after_model_change(self, form, model, is_created):
        """Called when ACL has been changed."""
        try:
            current_explicit_acls.reindex_acl(model)
        except:
            traceback.print_exc()

    def after_model_delete(self, model):
        """Called when ACL has been deleted."""
        current_explicit_acls.reindex_acl_remove(model)


class ElasticsearchACLModelView(ACLModelViewMixin, ModelView):
    """ModelView for the elasticsearch ACLs."""

    column_formatters = dict(
    )
    column_details_list = (
        'id', 'name', 'record_selector', 'created', 'updated', 'originator', 'priority', 'operation')
    column_list = (
        'id', 'name', 'schemas', 'operation', 'record_selector', 'priority', 'created', 'updated', 'originator')
    column_labels = dict(
        id=_('ACL ID'),
        database_operations=_('Operations')
    )
    column_filters = ('created', 'updated',)
    column_searchable_list = ('name',)
    column_default_sort = 'name'
    form_base_class = FlaskForm
    form_columns = ('name', 'priority', 'schemas', 'operation', 'record_selector', 'actors')
    form_args = dict(
    )
    page_size = 25
    form_extra_fields = {
        'schemas': sqla.fields.QuerySelectMultipleField(
            label='Schemas',
            query_factory=schemas_choices,
            widget=Select2Widget(multiple=True),
            get_pk=lambda x: x,
        )
    }

    def validate_record_selector(self, form, field):
        """Checks that the record selector is valid and we can use it to perform query in elasticsearch index."""
        schemas = form.schemas.data
        record_selector = field.data
        if not record_selector:
            raise StopValidation(
                'Record selector must not be empty. If you want to match all resources, use {"match_all": {}}')
        try:
            for index in schemas:
                current_search_client.search(
                    index=index, size=0, body={
                        'query': record_selector
                    }
                )
        except Exception as e:
            raise StopValidation(str(e))


#
#
# def link_record(view, context, model, name):
#     recid = model.record_id
#     if recid:
#         href = url_for('recordmetadata.details_view', id=recid)
#         return Markup('<a href="{0}">{1}</a>'.format(
#             href, escape(model.record_str)))
#     else:
#         return model.record_str
#
#
class IdACLModelView(ACLModelViewMixin, ModelView):
    """ModelView for the ID ACLs."""

    column_formatters = dict(
        # record_str=link_record
    )
    column_details_list = (
        'id', 'name', 'record_str', 'schemas', 'created', 'updated', 'originator', 'priority', 'operation')
    column_list = ('id', 'name', 'operation', 'record_str', 'priority', 'created', 'updated', 'originator')
    column_labels = dict(
        id=_('ACL ID'),
        record_str=_('Record')
    )
    column_filters = ('created', 'updated',)
    column_searchable_list = ('name',)
    column_default_sort = 'name'
    form_base_class = FlaskForm
    form_columns = ('name', 'priority', 'record_id', 'schemas', 'operation', 'actors')
    form_args = dict(
    )
    page_size = 25
    form_extra_fields = {
        'schemas': sqla.fields.QuerySelectMultipleField(
            label='Schemas',
            query_factory=schemas_choices,
            widget=Select2Widget(multiple=True),
            get_pk=lambda x: x,
        )
    }

    def validate_form(self, form):
        """Validator that fills in schema from the record if not yet already filled."""
        if not super().validate_form(form):
            return False
        if hasattr(form, 'schemas'):
            schemas = form.schemas.data
            if not schemas:

                record_id = form.record_id.data
                try:
                    rec = Record.get_record(record_id)
                except:
                    form.schemas.errors.append('No schemas defined and the record with the given does not exist yet')
                    return False

                form.schemas.data = [
                    rec.get('$schema', '')
                ]

        return True


class DefaultACLModelView(ACLModelViewMixin, ModelView):
    """ModelView for the default ACLs."""

    column_formatters = dict(
        # record_str=link_record
    )
    column_details_list = (
        'id', 'name', 'schemas', 'created', 'updated', 'originator', 'priority', 'operation')
    column_list = ('id', 'name', 'schemas', 'operation', 'priority', 'created', 'updated', 'originator')
    column_labels = dict(
        id=_('ACL ID'),
    )
    column_filters = ('created', 'updated',)
    column_searchable_list = ('name',)
    column_default_sort = 'name'
    form_base_class = FlaskForm
    form_columns = ('name', 'priority', 'schemas', 'operation', 'actors')
    form_args = dict(
    )
    page_size = 25
    form_extra_fields = {
        # 'schemas': StringArrayField(),
        'schemas': sqla.fields.QuerySelectMultipleField(
            label='Schemas',
            query_factory=schemas_choices,
            widget=Select2Widget(multiple=True),
            get_pk=lambda x: x,
        )
    }


class PropertyValueModelForm(OriginatorMixin, InlineFormAdmin):
    """ModelView for ACL Property Values."""

    # form_base_class = FlaskForm
    form_columns = ('id', 'name', 'value', 'match_operation', 'bool_operation')
    form_extra_fields = {
        'match_operation': SelectField(
            choices=[(op.value, op.name) for op in MatchOperation],
            label=_('Value matching Operation'),
            widget=Select2Widget(multiple=False),
        ),
        'bool_operation': SelectField(
            choices=[(op.value, op.name) for op in BoolOperation],
            label=_('Bool filter Operation'),
            widget=Select2Widget(multiple=False),
        )
    }


class PropertyValueACLModelView(ACLModelViewMixin, ModelView):
    """ModelView for Property based ACLs."""

    column_formatters = dict()
    column_details_list = (
        'id', 'name', 'schemas', 'created', 'updated', 'originator', 'priority', 'operation', 'property_values')
    column_list = ('name', 'schemas', 'operation', 'priority', 'actors', 'created', 'updated', 'originator')
    column_labels = dict(
        id=_('ACL ID'),
        property_value = _('Properties')
    )
    column_filters = ('created', 'updated',)
    column_searchable_list = ('name',)
    column_default_sort = 'name'
    form_base_class = FlaskForm
    form_columns = ('name', 'priority', 'schemas', 'operation', 'actors')
    form_args = dict(
    )
    page_size = 25
    form_extra_fields = {
        'schemas': sqla.fields.QuerySelectMultipleField(
            label='Schemas',
            query_factory=schemas_choices,
            widget=Select2Widget(multiple=True),
            get_pk=lambda x: x,
        )
    }
    inline_models = (PropertyValueModelForm(PropertyValue),)


class UserActorModelView(OriginatorMixin, ModelView):
    """ModelView for user actors."""

    column_formatters = dict(
        # record_str=link_record
    )
    column_details_list = (
        'id', 'name', 'users', 'created', 'updated', 'originator')
    column_list = ('id', 'name', 'users', 'created', 'updated', 'originator')
    column_labels = dict(
        id=_('ACL ID'),
        record_str=_('Record')
    )
    column_filters = ('created', 'updated',)
    column_searchable_list = ()
    column_default_sort = 'created'
    form_base_class = FlaskForm
    form_columns = ('users', 'name',)
    form_args = dict(
    )
    page_size = 25
    form_extra_fields = {
    }

    def on_model_change(self, form, model, is_created):
        """Sets up name if it has not been filled."""
        super().on_model_change(form, model, is_created)
        if not model.name:
            model.name = ', '.join([u.email for u in model.users])


class RoleActorModelView(OriginatorMixin, ModelView):
    """ModelView for role actors."""

    column_formatters = dict(
        # record_str=link_record
    )
    column_details_list = (
        'id', 'name', 'roles', 'created', 'updated', 'originator')
    column_list = ('id', 'name', 'roles', 'created', 'updated', 'originator')
    column_labels = dict(
        id=_('ACL ID'),
        record_str=_('Record')
    )
    column_filters = ('created', 'updated',)
    column_searchable_list = ()
    column_default_sort = 'created'
    form_base_class = FlaskForm
    form_columns = ('roles', 'name',)
    form_args = dict(
    )
    page_size = 25
    form_extra_fields = {
    }

    def on_model_change(self, form, model, is_created):
        """Sets up name if it has not been filled."""
        super().on_model_change(form, model, is_created)
        if not model.name:
            model.name = ', '.join([role.name for role in model.roles])


class SystemRoleActorModelView(OriginatorMixin, ModelView):
    """ModelView for role actors."""

    column_formatters = dict(
        # record_str=link_record
    )
    column_details_list = (
        'id', 'name', 'system_role', 'created', 'updated', 'originator')
    column_list = ('id', 'name', 'system_role', 'created', 'updated', 'originator')
    column_labels = dict(
        id=_('ACL ID'),
        record_str=_('Record')
    )
    column_filters = ('created', 'updated',)
    column_searchable_list = ()
    column_default_sort = 'created'
    form_base_class = FlaskForm
    form_columns = ('name', 'system_role')
    form_args = dict(
    )
    page_size = 25
    form_extra_fields = {
    }

    def on_model_change(self, form, model, is_created):
        """Sets up name if it has not been filled."""
        super().on_model_change(form, model, is_created)
        if not model.name:
            model.name = model.role


elasticsearch_aclset_adminview = dict(
    modelview=ElasticsearchACLModelView,
    model=ElasticsearchACL,
    category=_('ACLs'))

id_aclset_adminview = dict(
    modelview=IdACLModelView,
    model=IdACL,
    category=_('ACLs'))

default_aclset_adminview = dict(
    modelview=DefaultACLModelView,
    model=DefaultACL,
    category=_('ACLs'))

propertyvalueacl_aclset_adminview = dict(
    modelview=PropertyValueACLModelView,
    model=PropertyValueACL,
    category=_('ACLs'))

useractor_aclset_adminview = dict(
    modelview=UserActorModelView,
    model=UserActor,
    category=_('ACL Actors'))

roleactor_aclset_adminview = dict(
    modelview=RoleActorModelView,
    model=RoleActor,
    category=_('ACL Actors'))

systemroleactor_aclset_adminview = dict(
    modelview=SystemRoleActorModelView,
    model=SystemRoleActor,
    category=_('ACL Actors'))
