# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   sab 29 ott 2016 00:21:14 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

# This is adapted from
# http://docs.sqlalchemy.org/en/latest/_modules/examples/generic_associations/generic_fk.html

import sys

from sqlalchemy import create_engine, Integer, Column, String, and_, event, tuple_
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.orm import relationship, foreign, remote, backref, object_mapper


class GenericFKComparator(Comparator):
    def __eq__(self, other):
        mapper = object_mapper(other)
        pkeyv = mapper.primary_key_from_instance(other)
        return self.__clause_element__() == tuple_(other.__class__.__name__, pkeyv[0])


@as_declarative()
class Base(object):
    "Base class which provides automated table name and surrogate primary key column."

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id = Column(Integer, primary_key=True)


class Address(Base):
    """The Address class.

    This represents all address records in a single table. An instance can be attached to any
    other arbitrary entity, referencing it thru its class name and primary key.
    """

    street = Column(String)
    city = Column(String)
    zip = Column(String)

    object_kind = Column(String)
    """Refers to the type of parent."""

    object_id = Column(Integer)
    """Refers to the primary key of the parent.

    This could refer to any table.
    """

    @hybrid_property
    def related_object(self):
        "Access to the related object choosing the appropriate relationship."
        if self.object_kind:
            return getattr(self, "_%s" % self.object_kind)

    @related_object.setter
    def related_object(self, object):
        "Set the related object using the appropriate relationship."
        object_kind = object.__class__.__name__
        setattr(self, "_%s" % object_kind, object)

    @related_object.expression
    def related_object(klass):
        return tuple_(klass.object_kind, klass.object_id)

    @related_object.comparator
    def related_object(klass):
        return GenericFKComparator(tuple_(klass.object_kind, klass.object_id))


class HasAddresses(object):
    """HasAddresses mixin, creates a relationship to
    the address_association table for each parent.
    """


@event.listens_for(HasAddresses, "mapper_configured", propagate=True)
def setup_listener(mapper, class_):
    name = class_.__name__
    object_kind = name
    class_.addresses = relationship(
        Address, primaryjoin=and_(
            class_.id == foreign(remote(Address.object_id)),
            Address.object_kind == object_kind
        ),
        backref=backref("_%s" % object_kind,
                        primaryjoin=remote(class_.id) == foreign(Address.object_id)
        ))

    @event.listens_for(class_.addresses, "append")
    def append_address(target, value, initiator):
        value.object_kind = object_kind


class Customer(HasAddresses, Base):
    name = Column(String)


class Supplier(HasAddresses, Base):
    company_name = Column(String)


url = 'sqlite:////tmp/testdbloady.sqlite'
e = create_engine(url)

if len(sys.argv) == 2:
    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    else:
        assert e.execute("SELECT count(*)"
                         " FROM supplier s"
                         " JOIN address a"
                         "  ON a.object_id = s.id AND a.object_kind = 'Supplier'") \
                .fetchone() == (1,)

        assert e.execute("SELECT count(*)"
                         " FROM customer c"
                         " JOIN address a"
                         "  ON a.object_id = c.id AND a.object_kind = 'Customer'") \
                .fetchone() == (1,)
