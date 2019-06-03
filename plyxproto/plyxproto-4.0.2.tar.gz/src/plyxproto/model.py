# Copyright 2017-present Open Networking Foundation and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from .helpers import Base, SourceElement


class PackageStatement(SourceElement):

    def __init__(self, name, linespan=None, lexspan=None, p=None):
        super(
            PackageStatement,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name']
        self.name = name
        Base.p(self.name, self)

    def accept(self, visitor):
        visitor.visit_PackageStatement(self)


class ImportStatement(SourceElement):

    def __init__(self, name, linespan=None, lexspan=None, p=None):
        super(
            ImportStatement,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name']
        self.name = name
        Base.p(self.name, self)

    def accept(self, visitor):
        visitor.visit_ImportStatement(self)


class OptionStatement(SourceElement):

    def __init__(self, name, value, linespan=None, lexspan=None, p=None):
        super(
            OptionStatement,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'value']
        self.name = name
        Base.p(self.name, self)
        self.value = value
        Base.p(self.value, self)

    def accept(self, visitor):
        visitor.visit_OptionStatement(self)


class FieldDirective(SourceElement):

    def __init__(self, name, value, linespan=None, lexspan=None, p=None):
        super(
            FieldDirective,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'value']
        self.name = name
        Base.p(self.name, self)
        self.value = value
        Base.p(self.value, self)

    def accept(self, visitor):
        if visitor.visit_FieldDirective(self):
            self.v(self.name, visitor)
            self.v(self.value, visitor)
            visitor.visit_FieldDirective_post(self)


class FieldType(SourceElement):

    def __init__(self, name, linespan=None, lexspan=None, p=None):
        super(
            FieldType,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name']
        self.name = name
        Base.p(self.name, self)

    def accept(self, visitor):
        if visitor.visit_FieldType(self):
            self.v(self.name, visitor)


class LinkDefinition(SourceElement):

    def __init__(
            self,
            link_type,
            src_port,
            name,
            through,
            dst_port,
            linespan=None,
            lexspan=None,
            p=None,
            reverse_id=None):
        super(
            LinkDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['link_type', 'src_port',
                         'name', 'dst_port', 'through']
        self.link_type = link_type
        Base.p(self.link_type, self)

        self.src_port = src_port
        Base.p(self.src_port, self)

        self.name = name
        Base.p(self.name, self)

        self.through = through
        Base.p(self.through, self)

        self.dst_port = dst_port
        Base.p(self.dst_port, self)

        self.reverse_id = reverse_id
        Base.p(self.reverse_id, self)

    def accept(self, visitor):
        visitor.visit_LinkDefinition(self)


class FieldDefinition(SourceElement):

    def __init__(
            self,
            field_modifier,
            ftype,
            name,
            policy,
            fieldId,
            fieldDirective,
            linespan=None,
            lexspan=None,
            p=None):
        super(
            FieldDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['field_modifier', 'ftype',
                         'name', 'fieldId', 'policy', 'fieldDirective']
        self.name = name
        Base.p(self.name, self)
        self.field_modifier = field_modifier
        Base.p(self.field_modifier, self)
        self.ftype = ftype
        Base.p(self.ftype, self)
        self.fieldId = fieldId
        self.policy = policy
        Base.p(self.policy, self)

        Base.p(self.fieldId, self)
        self.fieldDirective = fieldDirective
        Base.p(self.fieldDirective, self)

    def accept(self, visitor):
        if visitor.visit_FieldDefinition(self):
            self.v(self.name, visitor)
            self.v(self.field_modifier, visitor)
            self.v(self.ftype, visitor)
            self.v(self.fieldId, visitor)
            self.v(self.fieldDirective, visitor)
            visitor.visit_FieldDefinition_post(self)


class EnumFieldDefinition(SourceElement):

    def __init__(self, name, fieldId, linespan=None, lexspan=None, p=None):
        super(
            EnumFieldDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'fieldId']
        self.name = name
        Base.p(self.name, self)
        self.fieldId = fieldId
        Base.p(self.fieldId, self)

    def accept(self, visitor):
        if visitor.visit_EnumFieldDefinition(self):
            self.v(self.name, visitor)
            self.v(self.fieldId, visitor)


class ReduceDefinition(SourceElement):

    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(
            ReduceDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'body']
        self.name = name
        Base.p(self.name, self)
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_EnumDefinition(self):
            self.v(self.name, visitor)
            self.v(self.body, visitor)


class MapDefinition(SourceElement):

    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(
            MapDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'body']
        self.name = name
        Base.p(self.name, self)
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_EnumDefinition(self):
            self.v(self.name, visitor)
            self.v(self.body, visitor)


class PolicyDefinition(SourceElement):

    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(
            PolicyDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'body']
        self.name = name
        Base.p(self.name, self)
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_PolicyDefinition(self):
            self.v(self.name, visitor)
            self.v(self.body, visitor)


class EnumDefinition(SourceElement):

    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(
            EnumDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'body']
        self.name = name
        Base.p(self.name, self)
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_EnumDefinition(self):
            self.v(self.name, visitor)
            self.v(self.body, visitor)


class LinkSpec(SourceElement):

    def __init__(
            self,
            field_spec,
            link_spec,
            linespan=None,
            lexspan=None,
            p=None):
        super(LinkSpec, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['link_def', 'field_def']
        self.link_def = link_spec
        Base.p(self.link_def, self)
        self.field_def = field_spec
        Base.p(self.field_def, self)

    def accept(self, visitor):
        if visitor.visit_LinkSpec(self):
            self.v(self.link_def, visitor)
            self.v(self.field_def, visitor)
            visitor.visit_LinkSpec_post(self)


class MessageDefinition(SourceElement):

    def __init__(
            self,
            name,
            policy,
            bases,
            body,
            linespan=None,
            lexspan=None,
            p=None):
        super(
            MessageDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'policy', 'bases', 'body']

        self.name = name
        Base.p(self.name, self)

        self.policy = policy
        Base.p(self.policy, self)

        self.bases = bases
        Base.p(self.bases, self)

        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_MessageDefinition(self):
            self.v(self.name, visitor)
            self.v(self.bases, visitor)
            self.v(self.body, visitor)
            visitor.visit_MessageDefinition_post(self)


"""
class MessageDefinition(SourceElement):
    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(MessageDefinition, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'body']
        self.name = name
        Base.p(self.name, self)
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_MessageDefinition(self):
            self.v(self.name, visitor)
            self.v(self.body, visitor)
            visitor.visit_MessageDefinition_post(self)
"""


class MessageExtension(SourceElement):

    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(
            MessageExtension,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'body']
        self.name = name
        Base.p(self.name, self)
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_MessageExtension(self):
            self.v(self.name, visitor)
            self.v(self.body, visitor)
            visitor.visit_MessageExtension_post(self)


class MethodDefinition(SourceElement):

    def __init__(
            self,
            name,
            name2,
            name3,
            linespan=None,
            lexspan=None,
            p=None):
        super(
            MethodDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'name2', 'name3']
        self.name = name
        Base.p(self.name, self)
        self.name2 = name2
        Base.p(self.name, self)
        self.name3 = name3
        Base.p(self.name, self)

    def accept(self, visitor):
        if visitor.visit_MethodDefinition(self):
            self.v(self.name, visitor)
            self.v(self.name2, visitor)
            self.v(self.name3, visitor)
            visitor.visit_MethodDefinition_post(self)


class ServiceDefinition(SourceElement):

    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(
            ServiceDefinition,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['name', 'body']
        self.name = name
        Base.p(self.name, self)
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_ServiceDefinition(self):
            self.v(self.name, visitor)
            self.v(self.body, visitor)
            visitor.visit_ServiceDefinition_post(self)


class ExtensionsMax(SourceElement):
    pass


class ExtensionsDirective(SourceElement):

    def __init__(self, fromVal, toVal, linespan=None, lexspan=None, p=None):
        super(
            ExtensionsDirective,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['fromVal', 'toVal']
        self.fromVal = fromVal
        Base.p(self.fromVal, self)
        self.toVal = toVal
        Base.p(self.toVal, self)

    def accept(self, visitor):
        if visitor.visit_ExtensionsDirective(self):
            self.v(self.fromVal, visitor)
            self.v(self.toVal, visitor)
            visitor.visit_ExtensionsDirective_post(self)


class Literal(SourceElement):

    def __init__(self, value, linespan=None, lexspan=None, p=None):
        super(Literal, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['value']
        self.value = value

    def accept(self, visitor):
        visitor.visit_Literal(self)


class Name(SourceElement):

    def __init__(self, value, linespan=None, lexspan=None, p=None):
        super(Name, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['value']
        self.value = value
        self.deriveLex()

    def append_name(self, name):
        try:
            self.value = self.value + '.' + name.value
        except BaseException:
            self.value = self.value + '.' + name

    def deriveLex(self):
        if hasattr(self.value, "lexspan"):
            self.lexspan = self.value.lexspan
            self.linespan = self.value.linespan
        else:
            return

    def accept(self, visitor):
        visitor.visit_Name(self)


class DotName(Name):
    elements = []

    def __init__(self, elements, linespan=None, lexspan=None, p=None):
        super(DotName, self).__init__(
            '.'.join([str(x) for x in elements]), linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['elements']
        self.elements = elements
        self.deriveLex()

    def deriveLex(self):
        if isinstance(self.elements, list) and len(self.elements) > 0:
            self.lexspan = (min([x.lexspan[0] for x in self.elements if x.lexspan[0] != 0]), max(
                [x.lexspan[1] for x in self.elements if x.lexspan[1] != 0]))
            self.linespan = (min([x.linespan[0] for x in self.elements if x.linespan[0] != 0]), max(
                [x.linespan[1] for x in self.elements if x.linespan[1] != 0]))
        elif hasattr(self.elements, "lexspan"):
            self.lexspan = self.elements.lexspan
            self.linespan = self.elements.linespan
        else:
            return

    def accept(self, visitor):
        visitor.visit_DotName(self)


class ProtoFile(SourceElement):

    def __init__(self, body, linespan=None, lexspan=None, p=None):
        super(
            ProtoFile,
            self).__init__(
            linespan=linespan,
            lexspan=lexspan,
            p=p)
        self._fields += ['body']
        self.body = body
        Base.p(self.body, self)

    def accept(self, visitor):
        if visitor.visit_Proto(self):
            self.v(self.body, visitor)
            visitor.visit_Proto_post(self)
