# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Parsing of type definitions."""
import importlib
from ply import yacc
# Required for parser generation.
from . lexer import tokens  # NOQA
from . lexer import lexer as _lexer
from collections import OrderedDict
import six
import os
# Force preload of lexer and parser to avoid warning and regeneration by ply.
try:
    from . import types_parser as _types_parser  # NOQA
except ImportError:
    _types_parser = 'types_parser'

_outputdir = os.path.dirname(os.path.abspath(__file__))


@six.python_2_unicode_compatible
class TypeVar(object):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '=> {}:{}'.format(hash(self), str(self.value))


def _update_backref(mapping, oldkey, newkey, value):
    """
    Updates references to make oldkey and newkey refer to the same
    type varable.
    """
    oldrefs = mapping.setdefault(
        'backref', {}).setdefault(oldkey, set())

    newrefs = mapping.setdefault(
        'backref', {}).setdefault(newkey, set())

    for oldref in oldrefs:
        mapping[oldref] = value
        newrefs.add(oldref)
        mapping['backref'][oldref] = newrefs

    mapping[oldkey] = value
    newrefs.add(oldkey)

    mapping['backref'][oldkey] = newrefs


def match(dt1, dt2, mapping=None):
    """
    Check if dt1 and dt2 matches in mapping. Mapping is extended with new
    type values for generic types.

    Generic variables are identified using 'id' if it exists (is not None) and
    'name' otherwise.


    Parameters
    ----------

    dt1: Type
    dt2: Type
    mapping: Dict[str or int, TypeVar]


    Returns
    -------

    bool
        True if dt1 and dt2 match and False otherwise.


    Examples
    --------

    Basic matching:

    >>> match(from_string('sytable'), from_string('sytable'))
    True
    >>> match(from_string('sytext'), from_string('sytext'))
    True
    >>> match(from_string('sytable'), from_string('sytext'))
    False
    >>> match(from_string('sytable'), from_string('<a>'))
    True
    >>> match(from_string('<a>'), from_string('sytable'))
    True

    More complex matching:

    >>> match(from_string('(x:<a>, y:{<b>}, c:[<c>])'),
    ...       from_string('(x:sytable, y:{sytext}, c:[[sytable]])'))
    True

    Using mapping:

    >>> mapping = {}
    >>> match(from_string('(x:<a>, y:{<b>}, c:[<c>])'),
    ...       from_string('(x:sytable, y:{sytext}, c:[[sytable]])'), mapping)
    True
    >>> mapping
    {'a': => sytable, 'c': => [sytable], 'b': => sytext}

    >>> match(from_string('(x:<a>, y:{<b>}, c:[<c>])'),
    ...       from_string('(x:sytext, y:{sytable}, c:[[sytext]])'), mapping)
    False
    """

    assert(isinstance(dt1, Type))
    assert(isinstance(dt2, Type))

    def single_gen(gen, dt, mapping):
        ident = gen.id or gen.name()
        g = mapping.get(ident, None)

        if g is None:
            g = TypeVar()
            g.value = copy(dt)
            _update_backref(mapping, ident, ident, g)
            assert(dt is not None)
        else:
            if g.value is None:
                assert(dt is not None)
                g.value = copy(dt)
            else:
                return expr(g.value, dt, mapping)

        return True

    def update_key(key, value, mapping):
        visited = set()

        def inner(key):
            if key in visited:
                return
            visited.add(key)

            for key_ in mapping.get('const', {}).get(key, []):
                if mapping[key_] is not value:
                    mapping[key_] = value
                    inner(key_)

        inner(key)

    def double_gen(dt1, dt2, mapping):
        ident1 = dt1.id or dt1.name()
        ident2 = dt2.id or dt2.name()

        if ident1 == ident2:
            return True

        # mapping.setdefault(
        #     'const', {}).setdefault(ident1, set()).add(ident2)

        # mapping.setdefault(
        #     'const', {}).setdefault(ident2, set()).add(ident1)

        g1 = mapping.get(ident1, None)
        g2 = mapping.get(ident2, None)

        if g1 is None and g2 is None:
            # dt1 and dt2 are aliased.
            var = TypeVar()
            # mapping[ident1] = var
            # mapping[ident2] = var
            _update_backref(mapping, ident1, ident1, var)
            _update_backref(mapping, ident2, ident1, var)
        elif g1 is None:
            _update_backref(mapping, ident1, ident2, g2)
            # mapping[ident1] = g2
            # update_key(ident1, g2, mapping)
        elif g2 is None:
            _update_backref(mapping, ident2, ident1, g1)
            # mapping[ident2] = g1
            # update_key(ident2, g1, mapping)
        else:
            v1 = g1.value
            v2 = g2.value

            if v1 is None and v2 is None:
                _update_backref(mapping, ident2, ident1, g1)
                # update_key(ident1, g1, mapping)
            elif v1 is None:
                _update_backref(mapping, ident1, ident2, g2)
                # update_key(ident1, g2, mapping)
            elif v2 is None:
                _update_backref(mapping, ident2, ident1, g1)
                # update_key(ident2, g1, mapping)
            else:
                if not expr(g1.value, g2.value, mapping):
                    return False
                # newdt1 = instantiate(copy(g1.value), mapping)
                newdt = copy(g1.value)
                assert (newdt is not None)
                g1.value = newdt
                # update_key(ident1, g1, mapping)
                _update_backref(mapping, ident1, ident1, g1)
                _update_backref(mapping, ident2, ident1, g1)

        return True

    def expr(dt1, dt2, mapping):

        t1 = type(dt1)
        t2 = type(dt2)

        if t1 == t2:
            if t1 == TypeList:
                return expr(dt1[0], dt2[0], mapping)
            elif t1 == TypeDict:
                return expr(dt1.element(), dt2.element(), mapping)
            elif t1 == TypeRecord:
                if len(dt1.keys()) == len(dt2.keys()):
                    for dt1c, dt2c in zip(dt1.values(), dt2.values()):
                        if not expr(dt1c, dt2c, mapping):
                            return False
            elif t1 == TypeTuple:
                if len(dt1) == len(dt2):
                    for dt1c, dt2c in zip(dt1, dt2):
                        if not expr(dt1c, dt2c, mapping):
                            return False
                else:
                    return False
            elif t1 == TypeAlias:
                return dt1.name() == dt2.name()
            elif t1 == TypeGeneric:
                return double_gen(dt1, dt2, mapping)
            elif t1 == TypeFunction:
                return (expr(dt1.arg, dt2.arg, mapping) and
                        expr(dt1.result, dt2.result, mapping))
            return True

        elif t1 == TypeGeneric:
            return single_gen(dt1, dt2, mapping)

        elif t2 == TypeGeneric:
            return single_gen(dt2, dt1, mapping)
        return False

    if mapping is None:
        mapping = {}

    return expr(dt1, dt2, mapping)


def instantiate(dt, mapping):
    """
    Instantiate the type by recreating structure and replacing generic
    variables with their associated mapping value.


    Parameters
    ----------

    dt: Type
    mapping: Dict[str or int, TypeVar]


    Returns
    -------

    Type
        Rebuilt dt with generic variables replaced.


    Examples
    --------

    >>> instantiate(from_string('<a>'), {'a': TypeVar(from_string('sytable'))})
    sytable

    >>> instantiate(from_string('(x:<a>, y:[<b>])'),
    ...             {'a': TypeVar(from_string('sytable')),
    ...              'b': TypeVar(from_string('sytext'))})
    (x: sytable, y: [sytext])
    """
    assert(isinstance(dt, Type))
    visited = {}

    def inner(dt):
        visited_res = visited.get(dt)

        if visited_res:
            return visited_res

        visited[dt] = dt

        t = type(dt)

        if t == TypeList:
            res = TypeList([inner(dt[0])])

        elif t == TypeRecord:
            res = TypeRecord(OrderedDict((k, inner(v))
                                         for k, v in dt.items()))
        elif t == TypeDict:
            res = TypeDict(inner(dt.element))

        elif t == TypeTuple:
            res = TypeTuple(list(inner(v) for v in dt))

        elif t == TypeFunction:
            res = TypeFunction(inner(dt.arg), inner(dt.result))

        elif t == TypeGeneric:
            try:
                res = inner(mapping[dt.id or dt.name()].value)
                if res is None:
                    res = dt
            except KeyError:
                res = dt
        else:
            return dt

        visited[dt] = res
        return res

    result = inner(dt)
    if result is None:
        pass
    return result


_id_count = 0


def identify(dt, mapping):
    """Identify generic variables by giving them a new identifier unless the
    identifier is already in mapping. Once a new identifier is added, it is
    added to the mapping.

    It is desirable to use identify with the same mapping for different data
    types that are related with generic names that refer to the exact same
    type.

    One example of this would be an immagined pure and typed list append
    function:

    def append(element: T -> list: List[T] -> List[T]:

    Here all the T:s are related, they refer to the same thing. As a node this
    has 3 ports and uses lowercase a instead of T. After parsing these three
    types, applying identify for each of these three with the same mapping will
    make it so that all of the generic variables T will share the same id.

    Another separate function that uses T defines an unrelated T and shall
    not share identifier for T with append.


    Parameters
    ----------

    dt: Type
    mapping: Dict[str or int, int]


    Examples
    --------

    Shared mapping:

    >>> mapping = {}
    >>> dt1 = from_string('(x:<a>, y:<b>)')
    >>> dt2 = from_string('(x:<b>, y:<a>)')
    >>> identify(dt1, mapping)
    >>> identify(dt2, mapping)
    >>> dt1['x'].id == dt2['y'].id
    True
    >>> dt1['y'].id == dt2['x'].id
    True
    >>> dt1['x'].id != dt1['y'].id
    True

    Separate mapping:

    >>> mapping = {}
    >>> dt1 = from_string('(x:<a>, y:<b>)')
    >>> identify(dt1, mapping)
    >>> mapping = {}
    >>> dt2 = from_string('(x:<b>, y:<a>)')
    >>> identify(dt2, mapping)
    >>> dt1['x'].id == dt2['y'].id
    False
    >>> dt1['y'].id == dt2['x'].id
    False

    """

    assert(isinstance(dt, Type))
    global _id_count

    t = type(dt)

    if t == TypeList:
        identify(dt[0], mapping)

    elif t == TypeRecord:
        for v in dt.values():
            identify(v, mapping)

    elif t == TypeDict:
        identify(dt.element, mapping)

    elif t == TypeTuple:
        for v in dt:
            identify(v, mapping)

    elif t == TypeFunction:
        identify(dt.arg, mapping)
        identify(dt.result, mapping)

    elif t == TypeGeneric:
        ident = mapping.get(dt.name(), None)
        if ident is not None:
            dt.id = ident
        else:
            # Starts with 1 instead of 0 to simplify handling.
            _id_count += 1
            dt.id = _id_count
            mapping[dt.name()] = _id_count


def generics(dt):
    result = {}

    def inner(dt):
        assert(isinstance(dt, Type))
        t = type(dt)

        if t == TypeList:
            inner(dt[0])

        elif t == TypeRecord:
            for v in dt.values():
                inner(v)

        elif t == TypeDict:
            inner(v)

        elif t == TypeTuple:
            for v in dt:
                inner(v)

        elif t == TypeFunction:
            inner(dt.arg) or inner(dt.result)

        elif t == TypeGeneric:
            result[dt.id or dt.name()] = dt
    inner(dt)
    return result.values()


def copy(dt):
    """Copy dt, returning the copy."""
    assert(isinstance(dt, Type))

    t = type(dt)

    if t == TypeList:
        return TypeList([copy(dt[0])])

    elif t == TypeRecord:
        return TypeRecord(OrderedDict((k, copy(v))
                                      for k, v in dt.items()))
    elif t == TypeDict:
        return TypeDict(copy(dt.element))

    elif t == TypeTuple:
        return TypeTuple(list(copy(v) for v in dt))

    elif t == TypeFunction:
        return TypeFunction(copy(dt.arg), copy(dt.result))

    elif t == TypeGeneric:
        gt = TypeGeneric(dt.name())
        gt.id = dt.id
        return gt

    elif t == TypeAlias:
        return TypeAlias(dt.name())

    # Table and Text need not be copied.

    return dt


class Type(object):
    pass


class CustomComparable(object):
    """Base class that enables content based type comparison."""
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)


class TypeAlias(Type):
    """ A type representing a typealias """
    def __init__(self, name, definition=None):
        self._name = name
        self._definition = definition

    def name(self):
        """Returns the alias name."""
        return self._name

    def set_name(self, new_name):
        """Change the name of the typealias"""
        self._name = new_name

    def get(self):
        """Returns the definition of the type."""
        return self._definition

    def set(self, new_definition):
        """Set a new type definition"""
        self._definition = new_definition

    def __str__(self):
        return self._name

    def __repr__(self):
        if self._definition:
            return 'sytypealias {} = {}'.format(
                self._name, repr(self._definition))
        else:
            return self._name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name() == other.name()
        return False

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)


class TypeGeneric(Type):
    def __init__(self, name, id=None):
        self._name = name
        self.id = id

    def name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

    def __str__(self):
        return '<{}>'.format(self._name)

    def __repr__(self):
        return '<{}:{}>'.format(self._name, self.id or '')


class TypeRecord(Type, CustomComparable):
    """Type record."""
    def __init__(self, record=None):
        self._record = OrderedDict() if record is None else record

    def items(self):
        """Returns a list of all items in the record as (key, value)-tuples."""
        return self._record.items()

    def keys(self):
        """Returns a list of all record keys."""
        return self._record.keys()

    def value(self, key):
        """Returns the object matching key."""
        return self._record[key]

    def values(self):
        """Returns a list of all values."""
        return self._record.values()

    def __getitem__(self, key):
        """Returns the object matching key - invoked through record[key]."""
        return self.value(key)

    def __setitem__(self, key, value):
        """
        Sets the field of object matching key - invoked through
        record[key] = value.
        """
        self._record[key] = value

    def __str__(self):
        return "({0})".format(", ".join("{0}: {1}".format(*item)
                                        for item in self._record.items()))

    def __repr__(self):
        return "({0})".format(", ".join("{0}: {1}".format(str(item[0]),
                                                          repr(item[1]))
                                        for item in self._record.items()))


@six.python_2_unicode_compatible
class TypeTuple(Type, CustomComparable):
    def __init__(self, values):
        self.values = values

    def __str__(self):
        return "({0})".format(", ".join(str(value)
                                        for value in self.values))

    def __repr__(self):
        return "({0})".format(", ".join(repr(value)
                                        for value in self.values))

    def __iter__(self):
        for value in self.values:
            yield value

    def __getitem__(self, index):
        return self.values[index]

    def __setitem__(self, index, value):
        self.values[index] = value

    def __len__(self):
        return len(self.values)


class TypeDict(Type, CustomComparable):
    """A type representing a dictionary."""
    def __init__(self, element=None):
        self._elem = element

    def element(self):
        """Returns the contained element type."""
        return self._elem

    def set_element(self, elem):
        self._elem = elem

    def __str__(self):
        return "{" + "{0}".format(self._elem) + "}"

    def __repr__(self):
        return "{" + "{0}".format(repr(self._elem)) + "}"


class TypeList(Type, CustomComparable):
    """A type representing a list."""
    def __init__(self, items=None):
        """Init."""
        self._list = [] if items is None else items

    def __getitem__(self, index):
        """Get item."""
        return self._list[index]

    def __setitem__(self, index, value):
        self._list[index] = value
        return value

    def __add__(self, other_list):
        """
        Return a new list with the current extended list by other list
        using the '+' operator.
        """
        new_list = TypeList()
        new_list.extend(self)
        new_list.extend(other_list)
        return new_list

    def append(self, item):
        """Append item to list."""
        self._list.append(item)

    def items(self):
        """Returns all items in this list as a python list."""
        return self._list

    def extend(self, other_list):
        """Extend list with other list."""
        self._list.extend(other_list.items())

    def __str__(self):
        return '[{}]'.format(str(self._list[0]) if self._list else '')

    def __repr__(self):
        return '[{}]'.format(repr(self._list[0]) if self._list else '')


@six.python_2_unicode_compatible
class TypeFunction(Type, CustomComparable):
    """A type representing a list."""
    def __init__(self, arg, result):
        self.arg = arg
        self.result = result

    def __str__(self):
        if type(self.arg) == TypeFunction:
            return '({}) -> {}'.format(str(self.arg), str(self.result))
        return '{} -> {}'.format(str(self.arg), str(self.result))

    def __repr__(self):
        if type(self.arg) == TypeFunction:
            return '({}) -> {}'.format(repr(self.arg), repr(self.result))
        return '({}) -> {}'.format(repr(self.arg), repr(self.result))


class TypeVoid(Type, CustomComparable):
    def __repr__(self):
        return '()'


class TypeTable(Type):
    """A type representing a table."""
    def __init__(self):
        pass

    def __repr__(self):
        return "sytable"

    def __eq__(self, other):
        return isinstance(other, TypeTable)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)


class TypeText(Type):
    """A type representing text."""
    def __init__(self):
        pass

    def __repr__(self):
        return "sytext"

    def __eq__(self, other):
        return isinstance(other, TypeText)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)


def p_start(token):
    """
    start : definition
    """
    token[0] = token[1]


def p_primitive(token):
    """
    primitive : TEXT
              | TABLE
    """
    if token[1] == 'sytext':
        token[0] = TypeText()
    elif token[1] == 'sytable':
        token[0] = TypeTable()


def p_list(token):
    """
    list : LBRACKET type RBRACKET
    """
    token[0] = TypeList([token[2]])


def p_dict(token):
    """
    dict : LBRACE type RBRACE
    """
    token[0] = TypeDict(token[2])


def p_field(token):
    """
    field : IDENTIFIER COLON type
          | field COMMA IDENTIFIER COLON type
    """
    if len(token) > 4:
        rec = token[1]
        rec[token[3]] = token[5]
    else:
        rec = OrderedDict()
        rec[token[1]] = token[3]
    token[0] = rec


def p_record(token):
    """
    record : LPAREN field RPAREN
    """
    token[0] = TypeRecord(token[2])


def p_tuplefield(token):
    """
    tuplefield : COMMA type
               | COMMA type tuplefield
    """
    if len(token) > 3:
        tuplefield = token[3]
        tuplefield.insert(0, token[2])
        token[0] = tuplefield
    else:
        token[0] = [token[2]]


def p_tuple(token):
    """
    tuple : LPAREN RPAREN
          | LPAREN type tuplefield RPAREN
    """
    if len(token) > 4:
        tuplefield = token[3]
        tuplefield.insert(0, token[2])
        token[0] = TypeTuple(tuplefield)
    else:
        token[0] = TypeTuple(list())


def p_type(token):
    """
    type : primitive
         | list
         | dict
         | tuple
         | record
         | definition
         | typedefinition
         | generic
         | function
         | LPAREN type RPAREN
    """
    if len(token) == 2:
        token[0] = token[1]
    else:
        token[0] = token[2]


def p_function(token):
    """
    function : type ARROW type
    """
    token[0] = TypeFunction(token[1], token[3])


def p_typedefinition(token):
    """
    typedefinition : IDENTIFIER
    """
    ident = token[1]

    if manager.has_typealias_instance(ident):
        token[0] = manager.get_typealias_instance(ident)
    else:
        alias = TypeAlias(ident)
        token[0] = alias
        manager.set_typealias_instance(ident, alias)


def p_definition(token):
    """
    definition : ALIAS IDENTIFIER EQUALS type
    definition : ALIAS IDENTIFIER EQUALS type EOL
    """
    ident = token[2]

    if manager.has_typealias_definition(ident):
        alias = manager.get_typealias_definition(ident)
        alias.set(token[4])
        token[0] = alias
    else:
        alias = TypeAlias(ident, token[4])
        alias.set(token[4])
        token[0] = alias
        manager.set_typealias_definition(ident, alias)


def p_generic(token):
    """
    generic : LABRACKET IDENTIFIER RABRACKET
    """
    token[0] = TypeGeneric(token[2])


def p_error(token):
    raise TypeError(u'Invalid specification: "{}: {}"'.format(
        token.type, token.value))


class ParserOperations(object):
    """
    Base class for a lexer/parser that has the rules defined as methods.
    """

    def __init__(self, **kw):
        self.names = OrderedDict()

    def parse_line(self, line):
        """Feed a single line of text through the parser."""
        return parser.parse(line, lexer=_lexer)

    def parse_file(self, filename):
        """
        Feed a text file through the parser by successively calling
        parse_line() for each and every line in the file.
        """
        defs = []
        with open(filename) as fileobj:
            for line in fileobj:
                alias = self.parse_line(line)
                defs.append((alias.name(), alias))
            return defs


def parse_line(line):
    """
    Parse a single line containing a full type definition (multiple-line
    definitions aren't supported yet.
    >>> parse_line('sytypealias tables = [sytable]')
    sytypealias tables = [sytable]
    >>> parse_line('sytypealias records = (a: sytable, b: [sytable])')
    sytypealias records = (a: sytable, b: [sytable])
    """
    return typeparser.parse_line(line)


def parse_base_line(line):
    """
    Parse a single line containing a basic type definition (multiple-line
    definitions aren't supported yet.
    >>> parse_base_line('(a: sytable, b:[sytable])')
    (a: sytable, b: [sytable])
    """
    return parse_line('sytypealias type = {0}'.format(line)).get()


def parse_file(filename):
    """
    Parse a file containing a a number of type definitions.
    Returns a list of key value tuples where the key is the typealias name and
    the value the typealias itself.
    >>> open('test_file.txt', 'w').write('sytypealias tables = [sytable]')
    >>> parse_file('test_file.txt')
    [('tables', sytypealias tables = [sytable])]
    >>> import os; os.remove('test_file.txt')
    """
    return typeparser.parse_file(filename)


def normalize_definitions(definitions):
    """
    Normalize type definitions so that there is only one single instance of
    each type. Any normalized type is easy to traverse.
    """
    def expansions(dt):
        t = type(dt)

        if t == TypeList:
            value = dt[0]
            if isinstance(value, TypeAlias):
                dt[0] = definitions[value.name()]
            else:
                expansions(value)

        elif t == TypeDict:
            value = dt.element()
            if isinstance(value, TypeAlias):
                dt.set_element(definitions[value.name()])
            else:
                expansions(value)

        elif t == TypeRecord:
            for key, value in dt.items():
                if isinstance(value, TypeAlias):
                    dt[key] = definitions[value.name()]
                else:
                    expansions(value)

        elif t == TypeTuple:
            for i, value in enumerate(dt):
                if isinstance(value, TypeAlias):
                    dt[i] = definitions[value.name()]
                else:
                    expansions(value)

        elif t == TypeAlias:
            value = dt.get()
            if isinstance(value, TypeAlias):
                dt.set(definitions[value.name()])
            else:
                expansions(value)

    for value in definitions.values():
        expansions(value)


def normalize_instance(instance, normalized_definitions):
    """
    Normalize type instance according to the normalized definitions.
    TypeAlias instances will be replaced with definitions.
    """
    t = type(instance)

    if t == TypeAlias:
        try:
            return normalized_definitions[instance.name()]
        except KeyError:
            return instance

    elif t == TypeDict:
        instance.set_elements(normalize_instance(instance.elements(),
                                                 normalized_definitions))

    elif t == TypeRecord:
        for key, value in instance.items():
            instance[key] = normalize_instance(value, normalized_definitions)

    elif t == TypeList:
        instance[0] = normalize_instance(instance[0], normalized_definitions)

    return instance


def simplify_aliases(typealiases):
    """
    Takes a list of typealias() and expands inter-references to basic types.
    Returns an expanded list and a list of types that could not be fully
    expanded.
    """
    # First, make a dictionary of the list.
    aliases = {}
    for alias in typealiases:
        aliases[alias.name()] = alias

    def add_alias(ob_name, names):
        if ob_name in names:
            # typealias loop
            return None, None

        if ob_name in aliases:
            ret = aliases[ob_name].get()
        else:
            # Undefined reference - type is not in the supplied list
            ret = None
        names.append(ob_name)
        return ret, names

    # Recursive lookup of
    def traverse(ob, names_in_chain=None):
        names_in_chain = names_in_chain or []

        if type(ob) == type(TypeAlias('')):
            ret = traverse(ob.get(), names_in_chain)

        elif type(ob) == type(TypeList()):
            ret = TypeList()
            if type(ob[0]) == type(TypeAlias('')):
                intermediate, names_in_chain = add_alias(
                    ob[0].name(), names_in_chain)
                if not names_in_chain:
                    return None
                if intermediate:
                    ret.append(traverse(intermediate, names_in_chain))
                else:
                    ret.append(ob[0])
            else:
                ret.append(traverse(ob[0], names_in_chain))

        elif type(ob) == type(TypeRecord()):
            ret = TypeRecord()
            for name, member in ob.items():
                if type(member) == type(TypeAlias('')):
                    intermediate, names_in_chain = add_alias(
                        member.name(), names_in_chain)
                    if not names_in_chain:
                        return None
                    if intermediate:
                        ret[name] = traverse(intermediate, names_in_chain)
                    else:
                        ret[name] = ob
                else:
                    ret[name] = traverse(member, names_in_chain)
        else:
            ret = ob
        return ret

    for alias in sorted(aliases):
        aliases[alias] = TypeAlias(
            alias, traverse(aliases[alias].get(), [alias]))

    return aliases.items()


def simple_expand_type(typealiases, type_hierarchy):
    t = type(type_hierarchy)

    if t == TypeAlias:
        return expand_type(
            typealiases, typealiases[type_hierarchy.name()].get())

    copy(type_hierarchy)


def expand_type(typealiases, type_hierarchy):
    """
    Expands a type hierarchy that may contain type aliases into a new type
    hierarchy with the aliases replaced by primitive types.
    Returns expanded hierarchy.
    """
    t = type(type_hierarchy)

    if t == TypeAlias:
        return expand_type(
            typealiases, typealiases[type_hierarchy.name()].get())

    if t == TypeTable:
        return TypeTable()

    elif t == TypeText:
        return TypeText()

    elif t == TypeDict:
        return TypeDict(expand_type(typealiases, type_hierarchy.element()))

    elif t == TypeRecord:
        return TypeRecord(
            OrderedDict((key, expand_type(typealiases, value))
                        for key, value in type_hierarchy.items()))

    elif t == TypeList:
        return TypeList([expand_type(typealiases, item)
                         for item in type_hierarchy.items()])
    elif t == TypeTuple:
        return TypeTuple([expand_type(typealiases, value)
                          for value in type_hierarchy])
    elif t == TypeFunction:
        function = type_hierarchy
        functions = []

        while type(function) == TypeFunction:
            functions.append(function)
            function = function.result

        rfunciter = reversed(functions)
        lastfunction = six.next(rfunciter)
        function = TypeFunction(expand_type(typealiases, lastfunction.arg),
                                expand_type(typealiases, lastfunction.result))

        for function in rfunciter:
            function = TypeFunction(expand_type(typealiases, function.arg),
                                    function)
        return function
    elif t == TypeGeneric:
        return type_hierarchy
    else:
        assert(False)


def from_string(string_type, norm=True):
    parsed = parse_base_line(string_type)
    if norm:
        parsed = manager.normalize_instance(parsed)
    return parsed


def from_string_alias(string_alias_type):
    return manager.normalize_instance(parse_line(string_alias_type))


def from_string_expand(string_type):
    return manager.expand_type(from_string(string_type))


def from_type_expand(parsed_type):
    return manager.expand_type(parsed_type)


class TypesManager(object):
    def __init__(self):
        self._typealiases_instance = {}
        self._typealiases_definition = {}
        self._typealiases_util = {}
        self._typealiases_unloaded = {}

    def add_load_typealias(self, name, unparsed_dict):
        if name not in self._typealiases_util:
            module_name, class_path = unparsed_dict['util'].split(':')
            self._typealiases_unloaded[name] = (module_name, class_path)

            definition = parse_line(
                'sytypealias {} = {}'.format(name, unparsed_dict['type']))

            self._typealiases_definition[name] = definition

    def load_typealiases(self):
        self.normalize()
        for name, (module_name,
                   class_path) in self._typealiases_unloaded.items():

            util_class = importlib.import_module(module_name)
            for part_name in class_path.split('.'):
                util_class = getattr(util_class, part_name)
            self._typealiases_util[name] = util_class
            util_class.container_type = self._typealiases_definition[name]
        self._typealiases_unloaded.clear()

    def has_typealias_util(self, name):
        return name in self._typealiases_util

    def has_typealias_definition(self, name):
        return name in self._typealiases_definition

    def has_typealias_instance(self, name):
        return name in self._typealiases_instance

    def get_typealias_util(self, name):
        return self._typealiases_util[name]

    def get_typealias_definition(self, name):
        return self._typealiases_definition[name]

    def get_typealias_instance(self, name):
        return self._typealiases_instance[name]

    def set_typealias_util(self, name, value):
        self._typealiases_util[name] = value

    def set_typealias_definition(self, name, value):
        self._typealiases_definition[name] = value

    def set_typealias_instance(self, name, value):
        self._typealiases_instance[name] = value

    def normalize(self):
        normalize_definitions(
            self._typealiases_definition)

        self._typealiases_instance = {
            key: normalize_instance(value, self._typealiases_definition)
            for key, value in self._typealiases_instance.items()}

    def normalize_instance(self, value):
        if isinstance(value, TypeAlias):
            result = self._typealiases_definition[value.name()]
            value.set(result.get())
            return result
        else:
            return value

    def expand_type(self, value):
        return expand_type(self._typealiases_definition, value)


parser = yacc.yacc(debug=0,
                   optimize=1,
                   write_tables=1,
                   tabmodule=_types_parser,
                   outputdir=_outputdir)
typeparser = ParserOperations()
manager = TypesManager()
