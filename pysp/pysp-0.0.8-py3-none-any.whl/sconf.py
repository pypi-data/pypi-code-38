# -*- coding: utf-8 -*-

import codecs
import copy
import collections
import os
import re
import yaml

from pysp.serror import SDebug, SError


YNode = collections.namedtuple('YNode', 'xpath fullpath value')


class SYAML(SDebug):
    TAG_INCLUDE = '!include'
    MARK_INCLUDE = '__include__'
    EOL = '\n'

    @classmethod
    def dump(cls, yo, pretty=True):
        if pretty:
            return yaml.dump(yo, default_flow_style=False, indent=4)
        return yaml.dump(yo)

    def merge(self, newy, defy):
        if isinstance(newy, dict) and isinstance(defy, dict):
            for k, v in defy.items():
                if k not in newy:
                    # self.dprint(k, v)
                    newy[k] = v
                else:
                    newy[k] = self.merge(newy[k], v)  # if newy[k] else v
        return newy

    def load(self, yml, node_value=None):
        yaml.add_constructor(SYAML.TAG_INCLUDE, self.include)
        if os.path.exists(yml):
            with codecs.open(yml, 'r', encoding='utf-8') as fd:
                try:
                    # pass a file descripter, if use '!include' method
                    return self.store_mark(yaml.load(fd), yml, node_value)
                    # return yaml.load(fd)
                except yaml.YAMLError as e:
                    emsg = 'Error YAML Loading: %s\n%s' % (yml, str(e))
                    raise SError(emsg)
        try:
            return yaml.load(yml)
        except yaml.YAMLError as e:
            emsg = 'Error YAML Loading: %s\n%s' % (yml, str(e))
            raise SError(emsg)

    def collect_node(self, ymlo, xpath=''):
        ns = []
        self.dprint("xpath: '{}'".format(xpath))
        for k, v in ymlo.items():
            xp = xpath
            self.dprint('- ', k)
            if k == self.MARK_INCLUDE:
                self.dprint('+ ', xp)
                n = YNode(xpath=xp,
                          fullpath=ymlo[k]['fullpath'],
                          value=ymlo[k]['value'])
                ns.append(n)
            elif type(ymlo[k]) == dict:
                xp += ('.' if xp else '') + k
                ns += self.collect_node(ymlo[k], xp)
        return ns

    def _check_folder(self, path):
        dirname = os.path.dirname(os.path.abspath(path))
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def store(self, ymlo, pretty=True):
        '''Stored yml object to file.  In processing, yml object is changed.'''
        def store_file(ymlo, node):
            self._check_folder(node.fullpath)
            self.dprint('W: {}'.format(node.fullpath))
            with codecs.open(node.fullpath, 'w', encoding='utf-8') as fd:
                data = SYAML.dump(ymlo, pretty=pretty)
                for line in data.strip().splitlines():
                    if line.find(SYAML.TAG_INCLUDE) >= 0:
                        line = line.replace("'", "")
                    fd.write(line + SYAML.EOL)

        def get_node(ymlo, xpaths):
            ymlso = ymlo
            if xpaths and xpaths[0]:
                for k in xpaths:
                    ymlso = ymlso[k]
            return ymlso

        def store_node(ymlo, node):
            xpaths = node.xpath.split('.')
            ymlso = get_node(ymlo, xpaths)
            self.dprint('xpath={}, value={}'.format(node.xpath, node.value))
            self.dprint(SYAML.dump(ymlo, pretty=pretty))
            del ymlso[SYAML.MARK_INCLUDE]
            store_file(ymlso, node)

            ymlso = get_node(ymlo, xpaths[:-1])
            if node.value:
                ymlso[xpaths[-1]] = str(SYAML.TAG_INCLUDE + ' ' + node.value)
            self.dprint(SYAML.dump(ymlo, pretty=pretty))

        nodes = self.collect_node(ymlo)
        # self.DEBUG = True
        for n in nodes:
            self.dprint(f'{n.xpath}|{n.fullpath}|{n.value}')
            self.dprint('============')
            store_node(ymlo, n)

    def store_mark(self, yml, fullpath, node_value):
        if SYAML.MARK_INCLUDE in yml:
            emsg = 'Already use %s key in %s' % (SYAML.MARK_INCLUDE, fullpath)
            raise SError(emsg)
        yml[SYAML.MARK_INCLUDE] = {
            'fullpath': fullpath,
            'value': node_value
        }
        return yml

    def include(self, loader, node):
        # self.DEBUG = True
        fname = os.path.join(os.path.dirname(loader.name), node.value)
        self.dprint('Include YAML:', fname)
        return self.load(fname, node.value)


class SConfig(SYAML):
    _data = {}

    def __init__(self, yml_file=None):
        self._data = {}
        self._re_p = re.compile(r'([\w-]+)\[([-\d]+)\]')
        self._dirty = False
        if yml_file:
            self.loadup(yml_file)

    def dump(self):
        return super(SConfig, self).dump(self._data)

    def loadup(self, yml_file):
        if not os.path.exists(yml_file):
            raise SError('Not Exists: {}'.format(yml_file))
        if self._data:
            self.iprint('Overwrite')
        self._data = self.load(yml_file)

    def _fixup_folder(self, oyml, ymlpath):
        if ymlpath:
            nodes = self.collect_node(oyml)
            dirname = os.path.dirname(ymlpath)
            for n in nodes:
                if len(n.xpath.split('.')) > 1:
                    xpath = '{}.{}.fullpath'.format(n.xpath, self.MARK_INCLUDE)
                else:
                    xpath = '{}.fullpath'.format(self.MARK_INCLUDE)
                if n.value:
                    fpath = '{}/{}'.format(dirname, n.value)
                else:
                    fpath = ymlpath
                self.set_value(xpath, fpath, oyml=oyml)

    def collecting(self, yml_file):
        # if not os.path.exists(yml_file):
        #     raise SError('Not Exists: {}'.format(yml_file))
        if os.path.exists(yml_file):
            self._dirty = True
            newy = self.load(yml_file)
            self._data = self.merge(newy, self._data)
        self._fixup_folder(self._data, yml_file)

    def store(self, to_abs=None):
        data = copy.deepcopy(self._data)
        if to_abs:
            fullpath = os.path.abspath(to_abs)
            self.set_value(self.MARK_INCLUDE, {
                'fullpath': fullpath,
                'value': None
            }, oyml=data)
        self._fixup_folder(data, to_abs)
        if self._dirty:
            super(SConfig, self).store(data)

    def _parse_keylist(self, word):
        m = self._re_p.match(word)
        if m and m.lastindex == 2:
            return m.group(1), int(m.group(2))
        return None, 0

    def get_value(self, key, defvalue='', oyml=None):
        data = self._data if oyml is None else oyml
        for k in key.split('.'):
            if k in data:
                data = data[k]
                continue
            _k, _i = self._parse_keylist(k)
            if _k and _k in data and type(data[_k]) is list:
                try:
                    data = data[_k][_i]
                    continue
                except Exception:
                    pass
            return defvalue
        return data

    def set_value(self, key, value, oyml=None):
        self._dirty = True
        data = self._data if oyml is None else oyml
        karr = key.split('.')
        lenka = len(karr)
        for d, k in enumerate(karr):
            if k in data:
                if d == (lenka - 1):
                    data[k] = value
                else:
                    data = data[k]
                continue
            # keylist
            _k, _i = self._parse_keylist(k)
            if _k and _k in data and type(data[_k]) is list:
                if d == (lenka - 1):
                    try:
                        data[_k][_i] = value
                    except Exception:
                        # Append value to list,
                        # but it allows only the index is the next number
                        if len(data[_k]) == _i:
                            data[_k].append(value)
                            continue
                        raise SError('Index or Not Supported Format #1')
                else:
                    data = data[_k][_i]
                continue
            if _k:
                if _k not in data:
                    # Create a list value
                    if _i == 0:
                        data[_k] = []
                        data[_k].append(value)
                        continue
                raise SError('Index or Not Supported Format #2')
            # Others
            if d == (lenka - 1):
                data[k] = value
            else:
                data[k] = {}
                data = data[k]

    def delete(self, key, oyml=None):
        self._dirty = True
        data = self._data if oyml is None else oyml
        karr = key.split('.')
        lenka = len(karr)
        for d, k in enumerate(karr):
            if k in data:
                if d == (lenka - 1):
                    del data[k]
                else:
                    data = data[k]
                continue
            # keylist
            _k, _i = self._parse_keylist(k)
            if _k and _k in data and type(data[_k]) is list:
                if d == (lenka - 1):
                    try:
                        del data[_k][_i]
                    except IndexError:
                        raise SError('Index Out of Range')
                else:
                    data = data[_k][_i]
                continue
            # Others

    def dirty(self):
        if not self._dirty:
            self.dprint('Forcedly Set DIRTY')
        self._dirty = True
