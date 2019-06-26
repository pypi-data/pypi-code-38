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
Forms Core
"""

from __future__ import unicode_literals, absolute_import

import json
import datetime
import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import AssociationProxy, ASSOCIATION_PROXY

from rattail.time import localtime
from rattail.util import prettify, pretty_boolean, pretty_hours, pretty_quantity
from rattail.core import UNSPECIFIED

import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode
from colanderalchemy.schema import _creation_order
from deform import widget as dfwidget
from pyramid_deform import SessionFileUploadTempStore
from pyramid.renderers import render
from webhelpers2.html import tags, HTML

from tailbone.util import raw_datetime
from . import types
from .widgets import ReadonlyWidget, PlainDateWidget, JQueryDateWidget, JQueryTimeWidget


log = logging.getLogger(__name__)


def get_association_proxy(mapper, field):
    """
    Returns the association proxy corresponding to the given field name if one
    exists, or ``None``.
    """
    try:
        desc = getattr(mapper.all_orm_descriptors, field)
    except AttributeError:
        pass
    else:
        if desc.extension_type == ASSOCIATION_PROXY:
            return desc


def get_association_proxy_target(inspector, field):
    """
    Returns the property on the main class, which represents the "target"
    for the given association proxy field name.  Typically this will refer
    to the "extension" model class.
    """
    proxy = get_association_proxy(inspector, field)
    if proxy:
        proxy_target = inspector.get_property(proxy.target_collection)
        if isinstance(proxy_target, orm.RelationshipProperty) and not proxy_target.uselist:
            return proxy_target


def get_association_proxy_column(inspector, field):
    """
    Returns the property on the proxy target class, for the column which is
    reflected by the proxy.
    """
    proxy_target = get_association_proxy_target(inspector, field)
    if proxy_target:
        if proxy_target.mapper.has_property(field):
            prop = proxy_target.mapper.get_property(field)
            if isinstance(prop, orm.ColumnProperty) and isinstance(prop.columns[0], sa.Column):
                return prop


class CustomSchemaNode(SQLAlchemySchemaNode):

    def association_proxy(self, field):
        """
        Returns the association proxy corresponding to the given field name if
        one exists, or ``None``.
        """
        return get_association_proxy(self.inspector, field)

    def association_proxy_target(self, field):
        """
        Returns the property on the main class, which represents the "target"
        for the given association proxy field name.  Typically this will refer
        to the "extension" model class.
        """
        proxy = self.association_proxy(field)
        if proxy:
            proxy_target = self.inspector.get_property(proxy.target_collection)
            if isinstance(proxy_target, orm.RelationshipProperty) and not proxy_target.uselist:
                return proxy_target

    def association_proxy_column(self, field):
        """
        Returns the property on the proxy target class, for the column which is
        reflected by the proxy.
        """
        proxy_target = self.association_proxy_target(field)
        if proxy_target:
            prop = proxy_target.mapper.get_property(field)
            if isinstance(prop, orm.ColumnProperty) and isinstance(prop.columns[0], sa.Column):
                return prop

    def supported_association_proxy(self, field):
        """
        Returns boolean indicating whether the association proxy corresponding
        to the given field name, is "supported" with typical logic.
        """
        if not self.association_proxy_column(field):
            return False
        return True

    def add_nodes(self, includes, excludes, overrides):
        """
        Add all automatic nodes to the schema.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        if set(excludes) & set(includes):
            msg = 'excludes and includes are mutually exclusive.'
            raise ValueError(msg)

        # sorted to maintain the order in which the attributes
        # are defined
        properties = sorted(self.inspector.attrs, key=_creation_order)
        if excludes:
            if includes:
                raise ValueError("Must pass includes *or* excludes, but not both")
            supported = [prop.key for prop in properties
                         if prop.key not in excludes]
        elif includes:
            supported = includes
        elif includes is not None:
            supported = []

        for name in supported:
            prop = self.inspector.attrs.get(name, name)

            if name in excludes or (includes and name not in includes):
                log.debug('Attribute %s skipped imperatively', name)
                continue

            name_overrides_copy = overrides.get(name, {}).copy()

            if (isinstance(prop, orm.ColumnProperty)
                    and isinstance(prop.columns[0], sa.Column)):
                node = self.get_schema_from_column(
                    prop,
                    name_overrides_copy
                )
            elif isinstance(prop, orm.RelationshipProperty):
                if prop.mapper.class_ in self.parents_ and name not in includes:
                    continue
                node = self.get_schema_from_relationship(
                    prop,
                    name_overrides_copy
                )
            elif isinstance(prop, colander.SchemaNode):
                node = prop
            else:

                # magic for association proxy fields
                column = self.association_proxy_column(name)
                if column:
                    node = self.get_schema_from_column(column, name_overrides_copy)

                else:
                    log.debug(
                        'Attribute %s skipped due to not being '
                        'a ColumnProperty or RelationshipProperty',
                        name
                    )
                    continue

            if node is not None:
                self.add(node)

    def get_schema_from_relationship(self, prop, overrides):
        """ Build and return a :class:`colander.SchemaNode` for a relationship.
        """

        # for some reason ColanderAlchemy wants to crawl our entire ORM by
        # default, by way of relationships.  this 'excludes' hack is used to
        # prevent that, by forcing skip of 2nd-level relationships

        excludes = []
        if isinstance(prop, orm.RelationshipProperty):
            for next_prop in prop.mapper.iterate_properties:

                # don't include secondary relationships
                if isinstance(next_prop, orm.RelationshipProperty):
                    excludes.append(next_prop.key)

                # don't include fields of binary type
                elif isinstance(next_prop, orm.ColumnProperty):
                    for column in next_prop.columns:
                        if isinstance(column.type, sa.LargeBinary):
                            excludes.append(next_prop.key)

        if excludes:
            overrides['excludes'] = excludes

        return super(CustomSchemaNode, self).get_schema_from_relationship(prop, overrides)

    def dictify(self, obj):
        """ Return a dictified version of `obj` using schema information.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        dict_ = super(CustomSchemaNode, self).dictify(obj)
        for node in self:

            name = node.name
            if name not in dict_:
                # we're only processing association proxy fields here
                if not self.supported_association_proxy(name):
                    continue

                value = getattr(obj, name)
                if value is None:
                    if isinstance(node.typ, colander.String):
                        # colander has an issue with `None` on a String type
                        #  where it translates it into "None".  Let's check
                        #  for that specific case and turn it into a
                        #  `colander.null`.
                        dict_[name] = colander.null
                    else:
                        # A specific case this helps is with Integer where
                        #  `None` is an invalid value.  We call serialize()
                        #  to test if we have a value that will work later
                        #  for serialization and then allow it if it doesn't
                        #  raise an exception.  Hopefully this also catches
                        #  issues with user defined types and future issues.
                        try:
                            node.serialize(value)
                        except:
                            dict_[name] = colander.null
                        else:
                            dict_[name] = value
                else:
                    dict_[name] = value

        return dict_

    def objectify(self, dict_, context=None):
        """ Return an object representing ``dict_`` using schema information.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        mapper = self.inspector
        context = mapper.class_() if context is None else context
        for attr in dict_:
            if mapper.has_property(attr):
                prop = mapper.get_property(attr)
                if hasattr(prop, 'mapper'):
                    cls = prop.mapper.class_
                    if prop.uselist:
                        # Sequence of objects
                        value = [self[attr].children[0].objectify(obj)
                                 for obj in dict_[attr]]
                    else:
                        # Single object
                        value = self[attr].objectify(dict_[attr])
                else:
                     value = dict_[attr]
                     if value is colander.null:
                         # `colander.null` is never an appropriate
                         #  value to be placed on an SQLAlchemy object
                         #  so we translate it into `None`.
                         value = None
                setattr(context, attr, value)

            else:

                # try to process association proxy field
                if self.supported_association_proxy(attr):
                    value = dict_[attr]
                    if value is colander.null:
                        # `colander.null` is never an appropriate
                        #  value to be placed on an SQLAlchemy object
                        #  so we translate it into `None`.
                        value = None
                    setattr(context, attr, value)

                else:
                    # Ignore attributes if they are not mapped
                    log.debug(
                        'SQLAlchemySchemaNode.objectify: %s not found on '
                        '%s. This property has been ignored.',
                        attr, self
                    )
                    continue

        return context


class Form(object):
    """
    Base class for all forms.
    """
    save_label = "Save"
    update_label = "Save"
    show_cancel = True
    auto_disable = True
    auto_disable_save = True
    auto_disable_cancel = True

    def __init__(self, fields=None, schema=None, request=None, mobile=False, readonly=False, readonly_fields=[],
                 model_instance=None, model_class=None, appstruct=UNSPECIFIED, nodes={}, enums={}, labels={}, renderers=None,
                 hidden={}, widgets={}, defaults={}, validators={}, required={}, helptext={}, focus_spec=None,
                 action_url=None, cancel_url=None, use_buefy=None, component='tailbone-form'):

        self.fields = None
        if fields is not None:
            self.set_fields(fields)
        self.schema = schema
        if self.fields is None and self.schema:
            self.set_fields([f.name for f in self.schema])
        self.request = request
        self.mobile = mobile
        self.readonly = readonly
        self.readonly_fields = set(readonly_fields or [])
        self.model_instance = model_instance
        self.model_class = model_class
        if self.model_instance and not self.model_class and not isinstance(self.model_instance, dict):
            self.model_class = type(self.model_instance)
        if self.model_class and self.fields is None:
            self.set_fields(self.make_fields())
        self.appstruct = appstruct
        self.nodes = nodes or {}
        self.enums = enums or {}
        self.labels = labels or {}
        if renderers is None and self.model_class:
            self.renderers = self.make_renderers()
        else:
            self.renderers = renderers or {}
        self.hidden = hidden or {}
        self.widgets = widgets or {}
        self.defaults = defaults or {}
        self.validators = validators or {}
        self.required = required or {}
        self.helptext = helptext or {}
        self.focus_spec = focus_spec
        self.action_url = action_url
        self.cancel_url = cancel_url
        self.use_buefy = use_buefy
        self.component = component

    @property
    def component_studly(self):
        words = self.component.split('-')
        return ''.join([word.capitalize() for word in words])

    def __contains__(self, item):
        return item in self.fields

    def set_fields(self, fields):
        self.fields = FieldList(fields)

    def make_fields(self):
        """
        Return a default list of fields, based on :attr:`model_class`.
        """
        if not self.model_class:
            raise ValueError("Must define model_class to use make_fields()")

        mapper = orm.class_mapper(self.model_class)

        # first add primary column fields
        fields = FieldList([prop.key for prop in mapper.iterate_properties
                            if not prop.key.startswith('_')
                            and prop.key != 'versions'])

        # then add association proxy fields
        for key, desc in sa.inspect(self.model_class).all_orm_descriptors.items():
            if desc.extension_type == ASSOCIATION_PROXY:
                fields.append(key)

        return fields

    def make_renderers(self):
        """
        Return a default set of field renderers, based on :attr:`model_class`.
        """
        if not self.model_class:
            raise ValueError("Must define model_class to use make_renderers()")

        inspector = sa.inspect(self.model_class)
        renderers = {}

        # TODO: clearly this should be leaner...

        # first look at regular column fields
        for prop in inspector.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                if len(prop.columns) == 1:
                    column = prop.columns[0]
                    if isinstance(column.type, sa.DateTime):
                        renderers[prop.key] = self.render_datetime
                    elif isinstance(column.type, sa.Boolean):
                        renderers[prop.key] = self.render_boolean

        # then look at association proxy fields
        for key, desc in inspector.all_orm_descriptors.items():
            if desc.extension_type == ASSOCIATION_PROXY:
                prop = get_association_proxy_column(inspector, key)
                if prop:
                    column = prop.columns[0]
                    if isinstance(column.type, sa.DateTime):
                        renderers[key] = self.render_datetime
                    elif isinstance(column.type, sa.Boolean):
                        renderers[key] = self.render_boolean

        return renderers

    def append(self, field):
        self.fields.append(field)

    def insert_before(self, field, newfield):
        self.fields.insert_before(field, newfield)

    def insert_after(self, field, newfield):
        self.fields.insert_after(field, newfield)

    def replace(self, field, newfield):
        self.insert_after(field, newfield)
        self.remove(field)

    def remove(self, *args):
        for arg in args:
            if arg in self.fields:
                self.fields.remove(arg)

    # TODO: deprecare / remove this
    def remove_field(self, key):
        self.remove(key)

    # TODO: deprecare / remove this
    def remove_fields(self, *args):
        self.remove(*args)

    def make_schema(self):
        if not self.schema:

            if not self.model_class:
                # TODO
                raise NotImplementedError

            mapper = orm.class_mapper(self.model_class)

            # first filter our "full" field list so we ignore certain ones.  in
            # particular we don't want readonly fields in the schema, or any
            # which appear to be "private"
            includes = [f for f in self.fields
                        if f not in self.readonly_fields
                        and not f.startswith('_')
                        and f != 'versions']

            # derive list of "auto included" fields.  this is all "included"
            # fields which are part of the SQLAlchemy ORM for the object
            auto_includes = []
            property_keys = [p.key for p in mapper.iterate_properties]
            inspector = sa.inspect(self.model_class)
            for field in includes:
                if field in self.nodes:
                    continue    # these are explicitly set; no magic wanted
                if field in property_keys:
                    auto_includes.append(field)
                elif get_association_proxy(inspector, field):
                    auto_includes.append(field)

            # make schema - only include *property* fields at this point
            schema = CustomSchemaNode(self.model_class, includes=auto_includes)

            # for now, must manually add any "extra" fields?  this includes all
            # association proxy fields, not sure how other fields will behave
            for field in includes:
                if field not in schema:
                    node = self.nodes.get(field)
                    if not node:
                        node = colander.SchemaNode(colander.String(), name=field, missing='')
                    if not node.name:
                        node.name = field
                    schema.add(node)

            # apply any label overrides
            for key, label in self.labels.items():
                if key in schema:
                    schema[key].title = label

            # apply any widget overrides
            for key, widget in self.widgets.items():
                if key in schema:
                    schema[key].widget = widget

            # TODO: we are now doing this when making deform.Form, in which
            # case, do we still need to do it here?
            # apply any default values
            for key, default in self.defaults.items():
                if key in schema:
                    schema[key].default = default

            # apply any validators
            for key, validator in self.validators.items():
                if key in schema:
                    schema[key].validator = validator

            # apply required flags
            for key, required in self.required.items():
                if key in schema:
                    if required:
                        schema[key].missing = colander.required
                    else:
                        schema[key].missing = None # TODO?

            self.schema = schema

        return self.schema

    def set_label(self, key, label):
        self.labels[key] = label

        # update schema if necessary
        if self.schema and key in self.schema:
            self.schema[key].title = label

    def get_label(self, key):
        return self.labels.get(key, prettify(key))

    def set_readonly(self, key, readonly=True):
        if readonly:
            self.readonly_fields.add(key)
        else:
            if key in self.readonly_fields:
                self.readonly_fields.remove(key)

    def set_node(self, key, nodeinfo, **kwargs):
        if isinstance(nodeinfo, colander.SchemaNode):
            node = nodeinfo
        else:
            kwargs.setdefault('name', key)
            node = colander.SchemaNode(nodeinfo, **kwargs)
        self.nodes[key] = node

    def set_type(self, key, type_, **kwargs):
        if type_ == 'datetime':
            self.set_renderer(key, self.render_datetime)
        elif type_ == 'datetime_local':
            self.set_renderer(key, self.render_datetime_local)
        elif type_ == 'date_plain':
            self.set_widget(key, PlainDateWidget())
        elif type_ == 'date_jquery':
            # TODO: is this safe / a good idea?
            # self.set_node(key, colander.Date())
            self.set_widget(key, JQueryDateWidget())
        elif type_ == 'time_jquery':
            self.set_node(key, types.JQueryTime())
            self.set_widget(key, JQueryTimeWidget())
        elif type_ == 'duration':
            self.set_renderer(key, self.render_duration)
        elif type_ == 'boolean':
            self.set_renderer(key, self.render_boolean)
            self.set_widget(key, dfwidget.CheckboxWidget())
        elif type_ == 'currency':
            self.set_renderer(key, self.render_currency)
        elif type_ == 'quantity':
            self.set_renderer(key, self.render_quantity)
        elif type_ == 'percent':
            self.set_renderer(key, self.render_percent)
        elif type_ == 'gpc':
            self.set_renderer(key, self.render_gpc)
        elif type_ == 'enum':
            self.set_renderer(key, self.render_enum)
        elif type_ == 'codeblock':
            self.set_renderer(key, self.render_codeblock)
            self.set_widget(key, dfwidget.TextAreaWidget(cols=80, rows=8))
        elif type_ == 'text':
            self.set_widget(key, dfwidget.TextAreaWidget(cols=80, rows=8))
        elif type_ == 'file':
            tmpstore = SessionFileUploadTempStore(self.request)
            kw = {'widget': dfwidget.FileUploadWidget(tmpstore),
                  'title': self.get_label(key)}
            if 'required' in kwargs and not kwargs['required']:
                kw['missing'] = colander.null
            self.set_node(key, colander.SchemaNode(deform.FileData(), **kw))
        else:
            raise ValueError("unknown type for '{}' field: {}".format(key, type_))

    def set_enum(self, key, enum, empty=None):
        if enum:
            self.enums[key] = enum
            self.set_type(key, 'enum')
            values = list(enum.items())
            if empty:
                values.insert(0, empty)
            self.set_widget(key, dfwidget.SelectWidget(values=values))
        else:
            self.enums.pop(key, None)

    def get_enum(self, key):
        return self.enums.get(key)

    # TODO: i don't think this is actually being used anywhere..?
    def set_enum_value(self, key, enum_key, enum_value):
        enum = self.enums.get(key)
        if enum:
            enum[enum_key] = enum_value

    def set_renderer(self, key, renderer):
        if renderer is None:
            if key in self.renderers:
                del self.renderers[key]
        else:
            self.renderers[key] = renderer

    def set_hidden(self, key, hidden=True):
        self.hidden[key] = hidden

    def set_widget(self, key, widget):
        self.widgets[key] = widget

        # update schema if necessary
        if self.schema and key in self.schema:
            self.schema[key].widget = widget

    def set_validator(self, key, validator):
        self.validators[key] = validator

    def set_required(self, key, required=True):
        """
        Set whether or not value is required for a given field.
        """
        self.required[key] = required

    def set_default(self, key, value):
        """
        Set the default value for a given field.
        """
        self.defaults[key] = value

    def set_helptext(self, key, value):
        """
        Set the help text for a given field.
        """
        self.helptext[key] = value

    def has_helptext(self, key):
        """
        Returns boolean indicating whether the given field has accompanying
        help text.
        """
        return key in self.helptext

    def render_helptext(self, key):
        """
        Render the help text for the given field.
        """
        return self.helptext[key]

    def render(self, template=None, **kwargs):
        if not template:
            if self.readonly and not self.use_buefy:
                template = '/forms/form_readonly.mako'
            else:
                template = '/forms/form.mako'
        context = kwargs
        context['form'] = self
        return render(template, context)

    def make_deform_form(self):
        if not hasattr(self, 'deform_form'):

            schema = self.make_schema()

            # TODO: we are still also doing this when making the schema, but
            # seems like this should be the right place instead?
            # apply any default values
            for key, default in self.defaults.items():
                if key in schema:
                    schema[key].default = default

            # get initial form values from model instance
            kwargs = {}
            # TODO: ugh, this is necessary to avoid some logic
            # which assumes a ColanderAlchemy schema i think?
            if self.appstruct is not UNSPECIFIED:
                if self.appstruct:
                    kwargs['appstruct'] = self.appstruct
            elif self.model_instance:
                if self.model_class:
                    kwargs['appstruct'] = schema.dictify(self.model_instance)
                else:
                    kwargs['appstruct'] = self.model_instance

            # create form
            form = deform.Form(schema, **kwargs)
            form.tailbone_form = self

            # set readonly widget where applicable
            for field in self.readonly_fields:
                if field in form:
                    form[field].widget = ReadonlyWidget()

            self.deform_form = form

        return self.deform_form

    def render_deform(self, dform=None, template=None, **kwargs):
        if not template:
            if self.use_buefy:
                template = '/forms/deform_buefy.mako'
            else:
                template = '/forms/deform.mako'

        if dform is None:
            dform = self.make_deform_form()

        # TODO: would perhaps be nice to leverage deform's default rendering
        # someday..? i.e. using Chameleon *.pt templates
        # return form.render()

        context = kwargs
        context['form'] = self
        context['dform'] = dform
        context.setdefault('form_kwargs', {})
        # TODO: deprecate / remove the latter option here
        if self.auto_disable_save or self.auto_disable:
            if self.use_buefy:
                context['form_kwargs']['@submit'] = 'submit{}'.format(self.component_studly)
            else:
                context['form_kwargs']['class_'] = 'autodisable'
        if self.focus_spec:
            context['form_kwargs']['data-focus'] = self.focus_spec
        context['request'] = self.request
        context['readonly_fields'] = self.readonly_fields
        context['render_field_readonly'] = self.render_field_readonly
        return render(template, context)

    def get_vuejs_model_value(self, field):
        """
        This method must return "raw" JS which will be assigned as the initial
        model value for the given field.  This JS will be written as part of
        the overall response, to be interpreted on the client side.
        """
        if isinstance(field.schema.typ, deform.FileData):
            # TODO: don't recall why "always null" here?
            return 'null'

        if isinstance(field.schema.typ, colander.Set):
            if field.cstruct is colander.null:
                return '[]'

        if field.cstruct is colander.null:
            return 'null'

        return json.dumps(field.cstruct)

    def messages_json(self, messages):
        dump = json.dumps(messages)
        dump = dump.replace("'", '&apos;')
        return dump

    def field_visible(self, field):
        if self.hidden and self.hidden.get(field):
            return False
        return True

    def render_field_readonly(self, field_name, **kwargs):
        """
        Render the given field completely, but in read-only fashion.

        Note that this method will generate the wrapper div and label, as well
        as the field value.
        """
        if field_name not in self.fields:
            return ''

        # TODO: fair bit of duplication here, should merge with deform.mako
        label = HTML.tag('label', self.get_label(field_name), for_=field_name)
        field = self.render_field_value(field_name) or ''
        field_div = HTML.tag('div', class_='field', c=[field])
        contents = [label, field_div]

        if self.has_helptext(field_name):
            contents.append(HTML.tag('span', class_='instructions',
                                     c=[self.render_helptext(field_name)]))

        return HTML.tag('div', class_='field-wrapper {}'.format(field_name), c=contents)

    def render_field_value(self, field_name):
        record = self.model_instance
        if self.renderers and field_name in self.renderers:
            return self.renderers[field_name](record, field_name)
        return self.render_generic(record, field_name)

    def render_generic(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return six.text_type(value)

    def render_datetime(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return raw_datetime(self.request.rattail_config, value)

    def render_datetime_local(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        value = localtime(self.request.rattail_config, value)
        return raw_datetime(self.request.rattail_config, value)

    def render_duration(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return pretty_hours(datetime.timedelta(seconds=value))

    def render_boolean(self, record, field_name):
        value = self.obtain_value(record, field_name)
        return pretty_boolean(value)

    def render_currency(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        try:
            if value < 0:
                return "(${:0,.2f})".format(0 - value)
            return "${:0,.2f}".format(value)
        except ValueError:
            return six.text_type(value)

    def render_quantity(self, obj, field):
        value = self.obtain_value(obj, field)
        if value is None:
            return ""
        return pretty_quantity(value)

    def render_percent(self, obj, field):
        value = self.obtain_value(obj, field)
        if value is None:
            return ""
        return "{:0.3f} %".format(value * 100)

    def render_gpc(self, obj, field):
        value = self.obtain_value(obj, field)
        if value is None:
            return ""
        return value.pretty()

    def render_enum(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        enum = self.enums.get(field_name)
        if enum and value in enum:
            return six.text_type(enum[value])
        return six.text_type(value)

    def render_codeblock(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return HTML.tag('pre', value)

    def obtain_value(self, record, field_name):
        if record:
            try:
                return record[field_name]
            except TypeError:
                return getattr(record, field_name, None)

        # TODO: is this always safe to do?
        elif self.defaults and field_name in self.defaults:
            return self.defaults[field_name]

    def validate(self, *args, **kwargs):
        if kwargs.pop('newstyle', False):
            # yay, new behavior!
            if hasattr(self, 'validated'):
                del self.validated
            if self.request.method != 'POST':
                return False

            # we assume data is in the form of POST params
            controls = self.request.POST.items()

            # but if not, we can try to parse request body as JSON
            if not controls:
                try:
                    controls = self.request.json_body.items()
                except ValueError:
                    # not a valid JSON body, so no data
                    controls = []

            dform = self.make_deform_form()
            try:
                self.validated = dform.validate(controls)
                return True
            except deform.ValidationFailure:
                return False

        else: # legacy behavior
            raise_error = kwargs.pop('raise_error', True)
            dform = self.make_deform_form()
            try:
                return dform.validate(*args, **kwargs)
            except deform.ValidationFailure:
                if raise_error:
                    raise


class FieldList(list):
    """
    Convenience wrapper for a form's field list.
    """

    def insert_before(self, field, newfield):
        i = self.index(field)
        self.insert(i, newfield)

    def insert_after(self, field, newfield):
        i = self.index(field)
        self.insert(i + 1, newfield)


@colander.deferred
def upload_widget(node, kw):
    request = kw['request']
    tmpstore = SessionFileUploadTempStore(request)
    return dfwidget.FileUploadWidget(tmpstore)


class SimpleFileImport(colander.Schema):
    """
    Schema for simple file import.  Note that you must bind your ``request``
    object to this schema, i.e.::

       schema = SimpleFileImport().bind(request=request)
    """
    filename = colander.SchemaNode(deform.FileData(),
                                   widget=upload_widget)
