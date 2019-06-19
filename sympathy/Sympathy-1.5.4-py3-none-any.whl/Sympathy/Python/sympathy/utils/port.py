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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import sys
import six
import collections
from . import context
from .. types import types
from .. types import factory


def _to_dict(obj):
    if isinstance(obj, six.text_type):
        return obj
    else:
        return obj.to_dict()


class SyExpr(object):
    @classmethod
    def name(cls):
        _name = cls.__name__.lower()
        if six.PY2:
            return _name.decode('ascii')
        else:
            return _name


@six.python_2_unicode_compatible
class SyType(SyExpr):
    def __str__(self):
        return '{}({})'.format(self.name(), self._arg)

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))


class SyTypes(SyType):
    def __init__(self, sy_group):
        assert isinstance(sy_group, SyGroup)
        self._arg = sy_group

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))


@six.python_2_unicode_compatible
class SyGeneric(SyType):
    def __init__(self, name):
        assert any(isinstance(name, t) for t in (six.text_type, SyLetters))
        self._arg = name

    def __str__(self):
        if isinstance(self._arg, six.text_type):
            return 'sygeneric("{}")'.format(self._arg)
        else:
            return 'sygeneric({})'.format(self._arg)

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))


class SyList(SyType):
    def __init__(self, elt_sytype):
        assert isinstance(elt_sytype, SyType)
        self._arg = elt_sytype


@six.python_2_unicode_compatible
class SyTuple(SyType):
    def __init__(self, *elt_sytypes):
        for elt_type in elt_sytypes:
            assert isinstance(elt_type, SyType)

        self._arg = elt_sytypes

    def __str__(self):
        return 'sytuple({})'.format(
            ', '.join(six.text_type(a) for a in self._arg))

    def to_dict(self):
        return tuple(['sytuple'] + [_to_dict(elt) for elt in self._arg])


@six.python_2_unicode_compatible
class SyIndex(SyExpr):
    def __str__(self):
        return 'syindex'

    def to_dict(self):
        return ('syindex',)


@six.python_2_unicode_compatible
class SyLetters(SyExpr):
    def __init__(self, sy_index):
        assert isinstance(sy_index, SyIndex)
        self._arg = sy_index

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'syletters({})'.format(six.text_type(self._arg))


@six.python_2_unicode_compatible
class SyGroup(SyExpr):
    def __init__(self, name):
        assert isinstance(name, six.text_type)
        self._arg = name

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'sygroup("{}")'.format(self._arg)


@six.python_2_unicode_compatible
class SyIGroup(SyGroup):
    def __init__(self, name):
        assert isinstance(name, six.text_type)
        self._arg = name

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'syigroup("{}")'.format(self._arg)


@six.python_2_unicode_compatible
class SyOGroup(SyGroup):
    def __init__(self, name):
        assert isinstance(name, six.text_type)
        self._arg = name

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'syogroup("{}")'.format(self._arg)


@six.python_2_unicode_compatible
class SyUnlist(SyExpr):
    def to_dict(self):
        return ('syunlist',)

    def sycall(self, arg):
        return arg[1:-1]

    def __str__(self):
        return 'syunlist'


@six.python_2_unicode_compatible
class SyMap(SyType):
    def __init__(self, expr, list_expr):
        self._arg = [expr, list_expr]

    def to_dict(self):
        return tuple([self.name()] + [_to_dict(elt) for elt in self._arg])

    def __str__(self):
        return 'symap({}, {})'.format(self._arg[0], self._arg[1])


sygeneric = SyGeneric
sytuple = SyTuple
sylist = SyList
sytypes = SyTypes
syletters = SyLetters
sygroup = SyGroup
syigroup = SyIGroup
syogroup = SyOGroup

syindex = SyIndex()
syunlist = SyUnlist()
symap = SyMap


_lookup = {
    syt.name(): syt for syt in
    [sygeneric, sytuple, sylist, sytypes, syletters,
     syigroup, syogroup, sygroup, syindex, syunlist, symap]}


class TemplateTypes(object):
    generic = sygeneric
    tuple = sytuple
    types = sytypes
    list = sylist
    letters = syletters
    group = sygroup
    igroup = syigroup
    ogroup = syogroup
    index = syindex
    unlist = syunlist
    map = symap


def _from_dict(obj):
    if isinstance(obj, tuple) or isinstance(obj, list):
        inst_or_cls = _lookup[obj[0]]
        if isinstance(inst_or_cls, SyExpr):
            return inst_or_cls
        elif issubclass(inst_or_cls, SyExpr):
            return inst_or_cls(*[_from_dict(arg) for arg in obj[1:]])
    elif isinstance(obj, six.text_type):
        return obj


def minno(no):
    if isinstance(no, int):
        return no
    elif no is None:
        return 1

    return minno(no[0])


def maxno(no):
    if isinstance(no, int):
        return no

    if len(no) == 1 or no[1] is None:
        return float('inf')

    return no[1] or no[0] or 1


def defno(no):
    if (isinstance(no, tuple) or isinstance(no, list)) and len(no) == 3:
        return no[2]
    return minno(no)


def eval_ports(ports):

    def eval_sygeneric(sytype, ctx):
        return '<{}>'.format(eval_sytype(sytype._arg, ctx))

    def eval_sytuple(sytype, ctx):
        args = [y for a in sytype._arg for y in eval_sytype(a, ctx)]
        return '({})'.format(','.join(args))

    def eval_sylist(sytype, ctx):
        return '[{}]'.format(eval_sytype(sytype._arg, ctx))

    def eval_syletters(sytype, ctx):
        i = eval_sytype(sytype._arg, ctx)
        oa = ord('a')
        assert i >= 0 and i <= ord('z') - oa
        return six.unichr(oa + i)

    def eval_sytypes(group, ctx):
        return tuple([a for a in eval_sytype(group._arg, ctx)])

    def eval_sygroup(sygroup, ctx):
        return [eval_port(port)['type'] for port in groups[sygroup._arg]]

    def eval_syigroup(sygroup, ctx):
        return [eval_port(port)['type'] for port in igroups[sygroup._arg]]

    def eval_syogroup(sygroup, ctx):
        return [eval_port(port)['type'] for port in ogroups[sygroup._arg]]

    def eval_syindex(sytype, ctx):
        return ctx['index']

    def eval_symap(sytype, ctx):
        return tuple(map(sytype._arg[0].sycall,
                         eval_sytype(sytype._arg[1], ctx)))

    eval_lookup = {'sygeneric': eval_sygeneric,
                   'sytuple': eval_sytuple,
                   'sytypes': eval_sytypes,
                   'sylist': eval_sylist,
                   'syletters': eval_syletters,
                   'sygroup': eval_sygroup,
                   'syigroup': eval_syigroup,
                   'syogroup': eval_syogroup,
                   'syindex': eval_syindex,
                   'symap': eval_symap}

    def eval_sytype(sytype, ctx):
        return eval_lookup[sytype.name()](sytype, ctx)

    def eval_port(port):
        if port['eval']:
            index = port['group_index']
            ctx = {'index': index}
            sytype = _from_dict(port['type'])

            if isinstance(sytype, SyExpr):
                port['type'] = eval_sytype(sytype, ctx)

        port['eval'] = False
        return port

    groups = {}
    igroups = {}
    ogroups = {}

    for i, port in enumerate(ports):
        name = port['name']
        kind = port['kind']
        if kind == 'input':
            group_ports = igroups.setdefault(name, [])
        elif kind == 'output':
            group_ports = ogroups.setdefault(name, [])

        all_group_ports = groups.setdefault(name, [])

        port['group_index'] = len(group_ports)
        group_ports.append(port)
        all_group_ports.append(port)

    res = [eval_port(port) for port in ports]
    for port in res:
        del port['group_index']
    return res


def instantiate(input_ports, output_ports, no=None):
    no = no or {}
    inputs = []
    outputs = []
    for kind, ports, res in [('input', input_ports, inputs),
                             ('output', output_ports, outputs)]:
        for i, port in enumerate(ports):
            port = dict(port)
            port['kind'] = kind
            port['def_index'] = i
            res.append(port)

    ports = []
    for kind, group in [('input', inputs), ('output', outputs)]:
        ports.extend([dict(p) for p in group for i in range(
            no.get(kind, {}).get(p.get('name')) or defno(p.get('n', 1)))])

    for i, port in enumerate(ports):
        if not port.get('name'):
            port['name'] = i

        port['eval'] = True

    ports = eval_ports(ports)
    inputs = []
    outputs = []

    for port in ports:
        if port['kind'] == 'input':
            inputs.append(port)
        elif port['kind'] == 'output':
            outputs.append(port)
        else:
            assert False, 'Unknown port kind.'

        port.pop('kind')
        if isinstance(port['name'], int):
            del port['name']

        for key in list(port.keys()):
            if key not in ['description', 'scheme', 'type', 'name',
                           'def_index']:
                port.pop(key)

    for ports in [inputs, outputs]:
        for i, port in enumerate(ports):
            port['index'] = i

    return inputs, outputs


@six.python_2_unicode_compatible
class Ports(object):
    def __init__(self, ports):
        self.ports = ports
        self._lookup = {port['name']: port
                        for port in self.ports if 'name' in port}

    def __getitem__(self, key):
        try:
            return self.ports[key]
        except TypeError:
            return self._lookup[key]

    def __iter__(self):
        for item in self.ports:
            yield item

    def __str__(self):
        return '\n'.join(six.text_type(item) for item in self)


@six.python_2_unicode_compatible
class PortType(object):
    """Port is the interface for ports."""

    required_fields = ['description', 'type', 'scheme']
    optional_fields = ['name', 'requiresdata', 'n']

    def __init__(self, description, port_type, scheme, **kwargs):
        self.description = description
        self.type = port_type
        self.scheme = scheme

        for key, value in kwargs.items():
            if key in self.optional_fields:
                setattr(self, key, value)

        if 'n' in kwargs:
            assert 'name' in kwargs, (
                "If argument n is provided then name must be also.")

    def to_dict(self):
        """
        Return dict contaning the required fields:
            'description'
            'type'
            'scheme'
        Optionally:
            'name'
            'n'
            'requiresdata'

        The values should all be of string type.
        """
        result = {}
        for key in self.required_fields + self.optional_fields:
            try:
                attr = getattr(self, key)
                if attr is not None:
                    result[key] = attr
            except:
                pass

        if isinstance(self.type, SyExpr):
            result['type'] = self.type.to_dict()

        return result

    @staticmethod
    def from_dict(data):
        required = collections.OrderedDict(
            (key, data[key]) for key in PortType.required_fields)
        optional = {}
        for key in PortType.optional_fields:
            if key in data:
                optional[key] = data[key]

        type_ = required.get('type')
        if isinstance(type_, dict):
            required['type'] = _from_dict(type_)

        return PortType(*required.values(), **optional)

    def __contains__(self, key):
        return (key in self.required_fields or
                key in self.optional_fields and hasattr(self, key))

    def __getitem__(self, key):
        if key in self:
            return getattr(self, key)

    def __str__(self):
        return '**{}** : {}\n    {}'.format(getattr(self, 'name', ''),
                                            self.type,
                                            self.description)


def make_list_port(port, changes=None):
    port_dict = port.to_dict()
    if changes:
        port_dict.update(changes)
    if 'name' not in port_dict:
        port_dict['name'] = None
    res = PortType.from_dict(port_dict)
    res.type = '[{}]'.format(port.type)
    return res


def CustomPort(port_type, description, name=None):
    return PortType(description, port_type, 'hdf5', name=name,
                    requiresdata=None)


class Port(object):
    """Provides staticmethods to create Ports for built in types."""

    @staticmethod
    def Table(description, name=None, **kwargs):
        return CustomPort('table', description, name)

    @staticmethod
    def Tables(description, name=None, **kwargs):
        return CustomPort('[table]', description, name)

    @staticmethod
    def TableDict(description, name=None, **kwargs):
        return CustomPort('{table}', description, name)

    @staticmethod
    def ADAF(description, name=None, **kwargs):
        return CustomPort('adaf', description, name)

    @staticmethod
    def ADAFs(description, name=None, **kwargs):
        return CustomPort('[adaf]', description, name)

    # Keep old names for backwards compatibility
    Adaf = ADAF
    Adafs = ADAFs

    @staticmethod
    def Figure(description, scheme=None, name=None, **kwargs):
        return PortType(description, 'figure', 'text', name=name, **kwargs)

    @staticmethod
    def Figures(description, scheme=None, name=None, **kwargs):
        return PortType(description, '[figure]', 'text', name=name, **kwargs)

    @staticmethod
    def Datasource(description, scheme=None, name=None, **kwargs):
        return PortType(description, 'datasource', 'text', name=name,
                        **kwargs)

    @staticmethod
    def Datasources(description, scheme=None, name=None, **kwargs):
        return PortType(description, '[datasource]', 'text', name=name,
                        **kwargs)

    @staticmethod
    def Text(description, name=None, **kwargs):
        return CustomPort('text', description, name)

    @staticmethod
    def Texts(description, name=None, **kwargs):
        return CustomPort('[text]', description, name)

    @staticmethod
    def Json(description, name=None, **kwargs):
        return CustomPort('json', description, name)

    @staticmethod
    def Jsons(description, name=None, **kwargs):
        return CustomPort('[json]', description, name)

    @staticmethod
    def Custom(port_type, description, name=None, scheme='hdf5', n=None):
        return PortType(description, port_type, scheme, name=name, n=n)


@six.python_2_unicode_compatible
class RunPorts(object):
    """
    Provides ways to access Ports.

    In addition to accessing by string key it is also possible to access using
    numeric indices.

    Ports with names can be accessed using getattr.
    """
    def __init__(self, ports, infos):
        self.__ports = ports
        self.__infos = infos
        self.__lookup = {info['name']: port
                         for port, info in zip(ports, infos) if 'name' in info}

    def __getitem__(self, key):
        try:
            result = self.nth(key)
        except (IndexError, TypeError):
            result = self.__lookup[key]
        except KeyError:
            raise KeyError('No port named: "{}"'.format(key))
        return result

    def __iter__(self):
        return iter(self.__ports)

    def __contains__(self, key):
        return six.text_type(key) in self.__lookup

    def __len__(self):
        return len(self.__ports)

    def __str__(self):
        return '\n'.join(six.text_type(PortType.from_dict(info))
                         for info in self.__infos)

    def group(self, name):
        return [port for port, info in
                zip(self.__ports, self.__infos) if info.get('name') == name]

    @property
    def first(self):
        return self.nth(0)

    @property
    def second(self):
        return self.nth(1)

    @property
    def third(self):
        return self.nth(2)

    @property
    def fourth(self):
        return self.nth(3)

    @property
    def fifth(self):
        return self.nth(4)

    def nth(self, n):
        return self.__ports[n]


_use_linking = True


def disable_linking():
    """
    Internal function for disabling linking.
    Do not use this in function in client code.

    It globally disables linking, currently used to avoid a known bug in h5py
    related to h5py.ExternalLink:s and open files.
    """
    global _use_linking
    _use_linking = False


def _dummy_port_maker(cls, *args, **kwargs):
    """
    Wraps and returns the result of port_maker.
    For arguments to use consult port_maker.

    In case of an exception a PortDummy will be returned,
    capturing the error.
    Otherwise the result will be the same as for port_maker.
    """
    try:
        return port_maker(*args, **kwargs)
    except:
        return cls(sys.exc_info())


def dummy_port_maker(*args, **kwargs):
    return _dummy_port_maker(context.PortDummy, *args, **kwargs)


def dummy_input_port_maker(*args, **kwargs):
    return _dummy_port_maker(context.InputPortDummy, *args, **kwargs)


def dummy_output_port_maker(*args, **kwargs):
    return _dummy_port_maker(context.OutputPortDummy, *args, **kwargs)


def port_maker(port_information, mode, link, expanded=False,
               managed=False, no_datasource=False):
    """
    Return maker for port.
    Typaliases should be simplified with intra-dependencies expanded.
    """
    link = link and _use_linking
    alias = port_information['type']

    if no_datasource:
        return factory.typefactory.from_type(types.from_string(alias))
    else:
        return port_type_maker(
            port_information,
            types.from_string(alias),
            mode,
            link,
            managed)


def port_type_maker(port_information, type_expanded, mode, link,
                    managed=False):
    """Return maker for port."""
    link = link and _use_linking
    uri = (
        '{scheme}://{resource}#type={type}&path=/&mode={mode}&link={link}')
    filled_uri = uri.format(scheme=port_information['scheme'],
                            resource=port_information['file'],
                            type=type_expanded,
                            mode=mode,
                            link=link)
    return factory.typefactory.from_url(filled_uri,
                                        managed=managed)


def typealiases_parser(typealiases):
    """Parse and return dictionary of typaliases."""
    return {alias:
            types.from_string_alias(
                'sytypealias {0} = {1}'.format(alias, value['type']))
            for alias, value in typealiases.items()}


def typealiases_expander(typealiases_parsed):
    """
    Return dictionary of typealiases.
    The intra-dependencies are expanded.
    """
    return dict(
        types.simplify_aliases(typealiases_parsed.values()))
