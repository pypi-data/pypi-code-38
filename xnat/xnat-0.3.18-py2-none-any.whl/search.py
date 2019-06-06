from __future__ import absolute_import
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree
import csv
import six

xdat_ns = "http://nrg.wustl.edu/security"
ElementTree.register_namespace("xdat", xdat_ns)


def and_(*args):
    return CompoundConstraint(tuple(args), 'AND')


def or_(*args):
    return CompoundConstraint(tuple(args), 'OR')


class SearchField(property):
    def __init__(self, search_class, field_name):
        self.search_class = search_class
        self.field_name = field_name

    def __repr__(self):
        return '<SearchField {}>'.format(self.identifier)

    @property
    def identifier(self):
        # For the search criteria (where this is used) any xsitype/field
        # can be used (no need for display fields)
        return '{}/{}'.format(self.search_class.__xsi_type__, self.field_name)

    def __eq__(self, other):
        return Constraint(self.identifier, '=', other)

    def __gt__(self, other):
        return Constraint(self.identifier, '>', other)

    def __ge__(self, other):
        return Constraint(self.identifier, '>=', other)

    def __lt__(self, other):
        return Constraint(self.identifier, '<', other)

    def __le__(self, other):
        return Constraint(self.identifier, '<=', other)

    def like(self, other):
        return Constraint(self.identifier, ' LIKE ', other)


class Query(object):
    def __init__(self, queried_class, xnat_session, constraints=None):
        self.queried_class = queried_class
        self.xnat_session = xnat_session
        self.constraints = constraints

    @property
    def xsi_type(self):
        return self.queried_class.__xsi_type__

    def filter(self, *constraints):
        if len(constraints) == 0:
            return self
        elif len(constraints) == 1:
            constraints = constraints[0]
        else:
            constraints = CompoundConstraint(constraints, 'AND')

        if self.constraints is not None:
            constraints = CompoundConstraint((self.constraints, constraints), 'AND')

        return Query(self.queried_class, self.xnat_session, constraints)

    def to_xml(self):
        # Create main elements
        bundle = ElementTree.Element(ElementTree.QName(xdat_ns, "bundle"))
        root_elem_name = ElementTree.SubElement(bundle, ElementTree.QName(xdat_ns, "root_element_name"))
        root_elem_name.text = self.xsi_type

        # Add search fields
        search_where = ElementTree.SubElement(bundle, ElementTree.QName(xdat_ns, "search_field"))
        element_name = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "element_name"))
        element_name.text = self.xsi_type
        field_id = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "field_ID"))
        # TODO: This has to come from the querying class somehow
        field_id.text = 'ID'
        sequence = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "sequence"))
        sequence.text = '0'
        type_ = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "type"))
        type_.text = 'string'
        header = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "header"))
        header.text = 'url'

        # Add criteria
        search_where = ElementTree.SubElement(bundle, ElementTree.QName(xdat_ns, "search_where"))
        search_where.set("method", "AND")
        if self.constraints is not None:
            search_where.append(self.constraints.to_xml())

        return bundle

    def to_string(self):
        return ElementTree.tostring(self.to_xml())

    def all(self):
        result = self.xnat_session.post('/data/search', format='csv', data=self.to_string())

        # Parse returned table
        csv_text = str(result.text)
        csv_dialect = csv.Sniffer().sniff(csv_text)
        data = list(csv.reader(csv_text.splitlines(), dialect=csv_dialect))
        header = data[0]

        data = [dict(zip(header, x)) for x in data[1:]]

        return data


class BaseConstraint(six.with_metaclass(ABCMeta, object)):
    @abstractmethod
    def to_xml(self):
        pass

    def to_string(self):
        return ElementTree.tostring(self.to_xml())

    def __or__(self, other):
        return CompoundConstraint((self, other), 'OR')

    def __and__(self, other):
        return CompoundConstraint((self, other), 'AND')


class CompoundConstraint(BaseConstraint):
    def __init__(self, constraints, operator):
        self.constraints = constraints
        self.operator = operator

    def to_xml(self):
        elem = ElementTree.Element(ElementTree.QName(xdat_ns, "child_set"))
        elem.set("method", self.operator)
        elem.extend(x.to_xml() for x in self.constraints)

        return elem


class Constraint(BaseConstraint):
    def __init__(self, identifier, operator, right_hand):
        self.identifier = identifier
        self.operator = operator
        self.right_hand = right_hand

    def __repr__(self):
        return '<Constrain {} {}({})>'.format(self.identifier,
                                              self.operator,
                                              self.right_hand)

    def to_xml(self):
        elem = ElementTree.Element(ElementTree.QName(xdat_ns, "criteria"))
        schema_loc = ElementTree.SubElement(elem, ElementTree.QName(xdat_ns, "schema_field"))
        operator = ElementTree.SubElement(elem, ElementTree.QName(xdat_ns, "comparison_type"))
        value = ElementTree.SubElement(elem, ElementTree.QName(xdat_ns, "value"))

        elem.set("override_value_formatting", "0")
        schema_loc.text = self.identifier
        operator.text = self.operator
        value.text = str(self.right_hand)

        return elem
