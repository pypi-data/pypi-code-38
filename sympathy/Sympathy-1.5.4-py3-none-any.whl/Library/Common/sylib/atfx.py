# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
import os
import struct
import six
import numpy as np
from lxml import etree


tag_name = '__tag__'


sequence_representation_enum = [
    'explicit',
    'implicit_constant',
    'implicit_linear',
    'implicit_saw',
    'raw_linear',
    'raw_polynomial',
    'formula',
    'external_component',
    'raw_linear_external',
    'raw_polynomial_external',
    'raw_linear_calibrated',
    'raw_linear_calibrated_external']


_dt_dict = {
    'DT_BOOLEAN': {'np_type': np.bool,
                   'format': 'b'},
    'DT_BYTE': {'np_type': np.int8,
                'format': 'b'},
    'DT_SHORT': {'np_type': np.int16,
                 'format': 'i'},
    'DT_LONG': {'np_type': np.int32,
                'format': 'l'},
    'DT_LONGLONG': {'np_type': np.int64,
                    'format': 'q'},
    'DT_FLOAT': {'np_type': np.float32,
                 'format': 'f'},
    'DT_DOUBLE': {'np_type': np.float64,
                  'format': 'd'},
    'IEEEFLOAT4': {'np_type': np.float32,
                   'format': 'f'},
    'IEEEFLOAT8': {'np_type': np.float64,
                   'format': 'd'},
    'DT_SHORT_BEO': {'np_type': np.int16,
                     'format': 'i'},
    'DT_LONG_BEO': {'np_type': np.int32,
                    'format': 'l'},
    'DT_LONGLONG_BEO': {'np_type': np.int64,
                        'format': 'q'},
    'IEEEFLOAT4_BEO': {'np_type': np.float32,
                       'format': 'f'},
    'IEEEFLOAT8_BEO': {'np_type': np.float64,
                       'format': 'd'},
    'DT_STRING': {'np_type': six.text_type,
                  'format': 's'},
    'DT_BYTESTR': {'np_type': six.binary_type,
                   'format': ''},
    'DT_BLOB': {'np_type': six.binary_type,
                'format': ''},
    None: {'np_type': lambda x: x, 'format': ''}}


def _lower_keys(dict_):
    for k, v in list(dict_.items()):
        try:
            dict_[k.lower()] = v
        except AttributeError:
            pass


_lower_keys(_dt_dict)


def _a_utf8string(value):
    return np.array([s[1] for s in value])


def _a_num(dtype):

    def inner(value):
        return np.array(value.split(), dtype=dtype)

    return inner


values_dict = {'A_UTF8STRING': _a_utf8string}

for i in [2, 4, 8]:
    values_dict['A_FLOAT{}'.format(i * 8)] = _a_num('f{}'.format(i))
    values_dict['A_INT{}'.format(i * 8)] = _a_num('i{}'.format(i))


def dt_to_array(datatype, value):
    """Return value as array of datatype."""
    foundtype = _dt_dict[datatype]['np_type']
    if isinstance(value, list) or isinstance(value, tuple):
        if foundtype == six.text_type:
            data_array = np.array(value)
        else:
            data_array = np.array(value, dtype=foundtype)
    else:
        if foundtype == six.text_type:
            data_array = np.array([value])
        else:
            data_array = np.array([value], dtype=foundtype)

    return data_array


def dt_to_value(datatype, value):
    """Return value as single datatype."""
    foundtype = _dt_dict[datatype]['np_type']
    return foundtype(value)


def binary_to_array(dirname, filename, info):
    """Read binary data."""
    block_size = info['blocksize']
    values_per_block = info['valperblock']
    file_offset = info['inioffset']
    nr_elements = info['length']
    data_type = info['type']
    block_offset = info['valoffsets']
    np_type = _dt_dict[data_type]['np_type']
    type_format = _dt_dict[data_type]['format']
    data_type_size = np.dtype(np_type).itemsize
    endian_format = '<'
    if 'BEO' in data_type.split('_'):
        endian_format = '>'

    with open(os.path.join(dirname, filename), 'rb') as data_file:
        data_file.seek(file_offset, os.SEEK_SET)
        if data_type.lower() == 'dt_string' and values_per_block is None:
            result = data_file.read(nr_elements).split('\x00')[:-1]

        elif block_size == values_per_block * data_type_size:
            block = data_file.read(data_type_size * nr_elements)
            string_format = '{0}{1}{2}'.format(
                endian_format, nr_elements, type_format)
            result = struct.unpack(string_format, block)

        else:
            result = []

            if data_type.lower() == 'dt_string' and block_offset == [0]:
                result = data_file.read(nr_elements).split('\x00')[:-1]
            else:
                nr_blocks = nr_elements // values_per_block
                string_format = '{0}{1}'.format(endian_format, type_format)
                for ii in six.moves.range(nr_blocks):
                    data_file.seek(ii * block_size, os.SEEK_SET)
                    for offset in block_offset:
                        data_file.seek(offset, os.SEEK_CUR)
                        block = data_file.read(data_type_size)
                        result.append(struct.unpack(string_format, block)[0])

        return result


def _ns(tag, name):
    return '{{{}}}{}'.format(tag.nsmap[None], name)


def _strip(name):
    return name.split('}')[-1]


def _to_list(elem):
    sub = list(elem)
    tag = _strip(elem.tag)

    if sub:
        return (tag, [_to_list(x) for x in elem])
    else:
        try:
            text = elem.text.strip()
        except AttributeError:
            text = ''

        return (tag, text)


def _to_dict(elem):
    res = {}
    for x in list(elem):
        value = list(x)
        if not value:
            try:
                value = x.text.strip()
            except AttributeError:
                value = ''
        else:
            value = _to_list(x)

        res[_strip(x.tag)] = value
    return res


def _to_dict_tag(elem):
    res = _to_dict(elem)
    res[tag_name] = _strip(elem.tag)
    return res


def _applelem_to_dict(applelem):
    attrs_map = {}
    base_map = {}

    for attr in applelem.findall(_ns(applelem, 'application_attribute')):
        attr_dict = _to_dict_tag(attr)
        name = attr_dict['name']
        attrs_map[name] = attr_dict
        base_name = attr_dict.get('base_attribute')
        if base_name:
            base_map[base_name] = name

    for rela in applelem.findall(_ns(applelem, 'relation_attribute')):
        rela_dict = _to_dict_tag(rela)
        name = rela_dict['name']
        attrs_map[name] = rela_dict
        base_name = rela_dict.get('base_relation')
        if base_name:
            base_map[base_name] = name

    return {
        'name': applelem.find(_ns(applelem, 'name')).text.strip(),
        'basetype': applelem.find(_ns(applelem, 'basetype')).text.strip(),
        'attrs': attrs_map,
        'base_map': base_map
    }


def _instelem_to_dict(instelem):
    return _to_dict_tag(instelem)


def _atfxroot_to_ctx(atfxroot):
    applelems = atfxroot.find(
        _ns(atfxroot, 'application_model')).findall(
            _ns(atfxroot, 'application_element'))
    instelems = iter(atfxroot.find(_ns(atfxroot, 'instance_data')))
    try:
        comps = atfxroot.find(
            _ns(atfxroot, 'files')).findall(_ns(atfxroot, 'component'))
    except AttributeError:
        comps = []

    doc = _to_dict(atfxroot.find(_ns(atfxroot, 'documentation')))

    applelem_map = {}
    comp_map = {}
    instelem_map = {}

    for comp in comps:
        comp_dict = _to_dict(comp)
        filename = comp_dict.get('filename')
        if filename and filename.startswith('.\\'):
            comp_dict['filename'] = filename[2:]
        comp_map[comp_dict['identifier']] = comp_dict

    for applelem in applelems:
        data = _applelem_to_dict(applelem)
        applelem_map[data['name']] = data

    for instelem in instelems:
        data = _instelem_to_dict(instelem)
        tag = data[tag_name]
        tag_map = instelem_map.setdefault(tag, {})
        tag_map[data[applelem_map[tag]['base_map']['id']]] = data

    cls_map = _clss_factory(applelem_map)
    instelem_objmap = {}

    ctx = {'applelems': applelem_map, 'backref': {}, 'doc': doc}

    for k, v in instelem_map.items():
        objs = instelem_objmap.setdefault(k, {})
        applelem = applelem_map[k]
        for ident, instelem in instelem_map[k].items():
            objs[ident] = cls_map[k](ctx, applelem, instelem)

    ctx.update({'comps': comp_map,
                'instelems': instelem_objmap})
    return ctx


def _filename_to_ctx(filename):

    with open(filename, 'rb') as atfx:
        atfxroot = etree.parse(atfx).getroot()
        ctx = _atfxroot_to_ctx(atfxroot)
        return ctx


def _clss_factory(applelems):
    def cls_factory(clss, applelems):
            name = applelem['name']
            cls = clss.get(name)
            if not cls:
                basetype = applelem['basetype']
                basecls = clss[basetype]
                cls = type(name, (basecls,), {})
            clss[name] = cls

    clss = {}

    for v in globals().values():
        if isinstance(v, type):
            clss[v.__name__] = v

    for applelem in applelems.values():
        cls_factory(clss, applelems)

    return clss


def _get_insts(ctx, cls):
    instelems = ctx['instelems']
    insts = list(instelems.get(cls) or [])
    for subcls, applelem in ctx['applelems'].items():
        if applelem['basetype'] == cls:
            insts.extend((instelems.get(subcls) or {}).values())
    return insts


def _cls_ref(ctx, cls, value, max_occurs=None):
    if max_occurs in ['Many', '*'] or max_occurs > '1':
        return [ctx['instelems'][cls][v]
                for v in value.split(' ')]
    else:
        return ctx['instelems'][cls][value]


def _cls_backref(ctx, iname, lname, icls, lcls, id_, max_occurs=None):
    cache = ctx['backref'].setdefault((icls, lcls, lname, iname), {})

    if not cache:
        if max_occurs in ['Many', '*'] or max_occurs > '1':
            for linst in ctx['instelems'][lcls].values():
                try:
                    raw_attr = linst.raw_attr(iname)
                except KeyError:
                    return []
                for iid in raw_attr.split(' '):
                    cache.setdefault(iid, []).append(linst)
        else:
            for linst in ctx['instelems'][lcls].values():
                try:
                    raw_attr = linst.raw_attr(iname)
                except KeyError:
                    return None
                iid = raw_attr
                cache[iid] = linst

    lcache = ctx['backref'].setdefault((icls, lcls, lname, iname, id_), [])
    if not lcache:
        for k, v in cache.items():
            if k == id_:
                lcache.append(v)

    if max_occurs in ['Many', '*'] or max_occurs > '1':
        return [r1 for r0 in lcache for r1 in r0]
    else:
        if lcache:
            return lcache[0]


def base_rela(dest):
    def outer(func):
        args = dest.split(':')
        # bcls = args[0]

        try:
            max_occurs = args[1]
        except:
            max_occurs = None

        def inner(self):
            bname = func.__name__
            lname = self._applelem['base_map'].get(bname, bname)
            lcls = self._applelem['attrs'][lname]['ref_to']
            lmax_occurs = self._applelem['attrs'][lname].get(
                'max_occurs', max_occurs)

            try:
                return _cls_ref(
                    self._ctx, lcls, self._instelem[lname], lmax_occurs)
            except KeyError:
                # No forward ref.
                pass

            iname = self._applelem['attrs'][lname]['inverse_name']
            icls = self._instelem[tag_name]
            id_ = six.text_type(self.id())

            return _cls_backref(
                self._ctx, iname, lname, icls, lcls, id_, lmax_occurs)

        return inner
    return outer


def base_attr(datatype):
    def outer(func):
        bname = func.__name__

        def inner(self):
            lname = self._applelem['base_map'].get(bname, bname)
            value = self._instelem[lname]
            if datatype.startswith('['):
                # TODO(Erik): Convert array type values.
                return value

            return _dt_dict[datatype]['np_type'](value)

        inner.__name__ = bname
        inner.datatype = datatype
        inner.field = True
        return inner
    return outer


class ApplicationModel(object):
    def __init__(self, filename):
        self._ctx = _filename_to_ctx(filename)

    def instances(self, cls):
        return _get_insts(self._ctx, cls)

    def components(self):
        return self._ctx['comps']

    def documentation(self):
        return self._ctx['doc']


class BaseElement(object):
    base_applelem = {}

    def __init__(self, ctx, applelem, instelem):
        self._ctx = ctx
        self._applelem = applelem
        self._instelem = instelem

    def base_cls(self):
        return self._applelem['basetype']

    @base_attr('DT_STRING')
    def name(self):
        pass

    @base_attr('DT_LONGLONG')
    def id(self):
        pass

    @base_attr('DT_STRING')
    def description(self):
        pass

    @base_attr('DT_STRING')
    def version(self):
        pass

    @classmethod
    def base_applelem(cls):
        for x in dir(cls):
            if hasattr(x, 'field'):
                obj = {'name': x.__name__}
                for field in ['datatype']:
                    if field in x:
                        obj[field] = x.field

    def get_attr(self, name):
        if (self._applelem['attrs'][name].get(tag_name) ==
                'application_attribute'):
            datatype = self._applelem['attrs'][name].get('datatype')
            return _dt_dict[datatype]['np_type'](self._instelem[name])
        raise KeyError('"{}" is not an application attribute')

    def get_attrs(self):
        res = {}
        for k in self._applelem['attrs']:
            try:
                res[k] = self.get_attr(k)
            except KeyError:
                pass
        return res

    def raw_attr(self, name):
        return self._instelem[name]


class AoEnvironment(BaseElement):

    @base_rela
    def tests(self):
        pass


class AoTestSequence(BaseElement):
    pass


class AoTestSequencePart(BaseElement):
    pass


class AoTestEquipment(BaseElement):
    pass


class AoTest(BaseElement):

    @base_rela('AoEnvironment')
    def environment(self):
        pass

    @base_rela('AoSubTest:*')
    def children(self):
        pass


class AoSubTest(BaseElement):

    @base_attr('DT_STRING')
    def external_references(self):
        pass

    @base_rela('AoTest')
    def parent_test(self):
        pass

    @base_rela('AoMesurement:*')
    def children(self):
        pass


class AoMeasurement(BaseElement):

    @base_attr('DT_STRING')
    def measurement_begin(self):
        pass

    @base_attr('DT_STRING')
    def external_references(self):
        pass

    @base_rela('AoSubTest')
    def test(self):
        pass

    @base_rela('AoMeasurementQuantity:*')
    def measurement_quantities(self):
        pass

    @base_rela('AoSubMatrix:*')
    def submatrices(self):
        pass


class AoMeasurementQuantity(BaseElement):

    @base_attr('DT_STRING')
    def datatype(self):
        pass

    @base_rela('AoMeasurement')
    def mesurement(self):
        pass

    @base_rela('AoUnit')
    def unit(self):
        pass

    @base_rela('AoQuantity')
    def quantity(self):
        pass

    @base_rela('AoLocalColumn:*')
    def local_columns(self):
        pass


class AoSubmatrix(BaseElement):

    @base_attr('DT_LONGLONG')
    def number_of_rows(self):
        pass

    @base_rela('AoMeasurement')
    def measurement(self):
        pass

    @base_rela('AoLocalColumn:*')
    def local_columns(self):
        pass


class AoLocalColumn(BaseElement):

    @base_attr('DT_LONGLONG')
    def global_flag(self):
        pass

    @base_attr('DT_STRING')
    def sequence_representation(self):
        pass

    @base_attr('DT_LONGLONG')
    def independent(self):
        pass

    @base_attr('DT_LONGLONG')
    def raw_datatype(self):
        pass

    @base_attr('[DT_FLOAT]')
    def generation_parameters(self):
        pass

    @base_attr('DT_SHORT')
    def flags(self):
        pass

    def values(self):
        bname = 'values'
        lname = self._applelem['base_map'].get(bname, bname)
        lattr = self._instelem[lname]
        return lattr[1][0]

    @base_attr('DT_LONGLONG')
    def valuesperblock(self):
        pass

    @base_attr('DT_LONGLONG')
    def value_offset(self):
        pass

    @base_attr('DT_STRING')
    def flags_filename_url(self):
        pass

    @base_attr('DT_LONGLONG')
    def flags_start_offset(self):
        pass

    @base_rela('AoSubMatrix')
    def submatrix(self):
        pass

    @base_rela('AoMeasurementQuantity')
    def measurement_quantity(self):
        pass

    @base_rela('AoExternalComponent')
    def external_component(self):
        pass


class AoParameter(BaseElement):

    @base_attr('DT_STRING')
    def pvalue(self):
        pass

    @base_attr('DT_STRING')
    def parameter_datatype(self):
        pass

    @base_rela('AoUnit')
    def unit(self):
        pass

    @base_rela('AoParameterSet')
    def parameter_set(self):
        pass


class AoParameterSet(BaseElement):

    @base_rela('AoParameter:*')
    def parameters(self):
        pass


class AoQuantity(BaseElement):

    @base_attr('DT_STRING')
    def datatype(self):
        pass

    @base_attr('DT_STRING')
    def default_mq_name(self):
        pass

    @base_attr('DT_SHORT')
    def default_rank(self):
        pass

    @base_attr('DT_SHORT')
    def default_dimension(self):
        pass

    @base_attr('DT_SHORT')
    def default_type_size(self):
        pass

    @base_rela('AoUnit')
    def default_unit(self):
        pass


class AoUnit(BaseElement):

    @base_attr('DT_FLOAT64')
    def factor(self):
        pass

    @base_attr('DT_LONGLONG')
    def offset(self):
        pass

    @base_rela('AoPhysicalDimension')
    def phys_dimension(self):
        pass

    @base_rela('AoMeasurementQuantity:*')
    def measurement_quantities(self):
        pass


class AoPhysicalDimension(BaseElement):

    @base_attr('DT_SHORT')
    def length_exp(self):
        pass

    @base_attr('DT_SHORT')
    def mass_exp(self):
        pass

    @base_attr('DT_SHORT')
    def time_exp(self):
        pass

    @base_attr('DT_SHORT')
    def current_exp(self):
        pass

    @base_attr('DT_SHORT')
    def molar_amount_exp(self):
        pass

    @base_attr('DT_SHORT')
    def luminous_intensity_exp(self):
        pass


class AoExternalComponent(BaseElement):

    @base_attr('DT_SHORT')
    def ordinal_number(self):
        pass

    @base_attr('DT_LONG')
    def component_length(self):
        pass

    @base_attr('DT_STRING')
    def filename_url(self):
        pass

    @base_attr('DT_STRING')
    def value_type(self):
        pass

    @base_attr('DT_LONG')
    def start_offset(self):
        pass

    @base_attr('DT_LONG')
    def block_size(self):
        pass

    @base_attr('DT_LONG')
    def valuesperblock(self):
        pass

    @base_attr('DT_LONG')
    def value_offset(self):
        pass

    @base_attr('DT_STRING')
    def flags_filename_url(self):
        pass

    @base_attr('DT_SHORT')
    def flags_start_offset(self):
        pass

    @base_rela('AoLocalColumn')
    def local_column(self):
        pass
