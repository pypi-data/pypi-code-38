from __future__ import (absolute_import, division, print_function, unicode_literals)

from prettytable import PrettyTable

from .klass_is import IS
from .klass_operator import Operator
from .klass_print import Print
from .klass_str import Str


class Data(object):

    def __init__(self, data, has_header=True, header=[], name='__NAME'):
        self.name = name
        header, lines = self._normalize_origin(data, has_header, header)
        self.lines = lines[::]
        self.header = header[::]

    def _normalize_origin(self, data, has_header, header):
        if not data:
            data = []
        lines = []
        in_header = header[::]
        if header and IS.list_of_values(header) and IS.list_of_values(data) and len(data) > len(header):
            data = [[x] for x in data]
        if IS.dict_of_dict(data):
            origin = data.copy()
            header = [self.name]
            for key, values in origin.items():
                for k in sorted(values.keys()):
                    if k not in header:
                        header.append(k)
            if in_header:
                header = Operator.unique_intersection(in_header, header)
            for key, values in origin.items():
                line = []
                for h in header:
                    if h == self.name:
                        line.append(key)
                    else:
                        line.append(values.get(h, None))
                lines.append(line)
        elif IS.dict_of_values(data):
            header = sorted(list(data.keys()))
            if in_header:
                header = Operator.unique_intersection(in_header, header)
            lines = [[data[k] for k in header]]
        elif IS.list_of_dict(data):
            origin = data[::]
            if origin:
                header = []
            for item in origin:
                for key in sorted(item.keys()):
                    if key not in header:
                        header.append(key)
            lines = []
            if in_header:
                header = Operator.unique_intersection(in_header, header)
            for item in origin:
                line = []
                for h in header:
                    line.append(item.get(h, None))
                lines.append(line)
        elif IS.list_of_list(data):
            origin = data[::]
            if origin and has_header and not header:
                header = origin[0]
                lines = origin[1:]
            else:
                lines = origin
        elif IS.list_of_values(data):
            origin = data[::]
            if origin and has_header and not header:
                header = origin
                lines = []
            else:
                lines = [origin]
        else:
            lines = []
            for item in data:
                lines.append([getattr(item, h, None) for h in header])
        return header, lines

    def get_lines(self):
        return self.lines

    def get_default_header(self):
        header = self.get_header()
        if not header and self.lines:
            header = [x for x in range(len(self.lines[0]))]
        return header

    def get_header(self):
        return self.header

    def get_pretty_table(self, pretty=True, add_index=False, grep=False, index=False):
        def t(v):
            if not pretty:
                return v
            if v is None:
                return '-'
            if isinstance(v, bool):
                return 'X' if v else ''
            return v

        header = self.get_default_header()
        if add_index:
            header = ['Index'] + header
        x = PrettyTable()
        if pretty:
            x.field_names = [Str(x).to_title() for x in header]
        else:
            x.field_names = header
        for f in x.field_names:
            x.align[f] = 'l'
        for i, item in enumerate(self.get_lines(), 1):
            if index and index != i:
                continue
            if add_index:
                item = [i] + item
            if grep and grep.lower() not in '{}'.format(item).lower():
                continue
            x.add_row([t(x) for x in item])
        return x

    def get_html(self, **kwargs):
        header = self.get_default_header()
        x = PrettyTable()
        x.field_names = header
        for i, item in enumerate(self.get_lines(), 1):
            x.add_row(item)
        return x.get_html_string(**kwargs)

    def to_list(self):
        res = []
        if self.header:
            res.append(self.header)
        if self.lines:
            res.append(self.lines)
        return res

    def to_dictlist(self):
        header = self.header
        res = []
        if not header and self.lines:
            header = [x for x in range(len(self.lines[0]))]
        for line in self.lines:
            if IS.list_of_list(line):
                for item in line:
                    res.append({k: v for k, v in zip(header, item)})
            else:
                res.append({k: v for k, v in zip(header, line)})
        return res

    def show(self, pretty=True, add_index=False, grep=False, index=False, header=False, footer=False, exit=False):
        Print.info(
            self.get_pretty_table(
                pretty=pretty,
                add_index=add_index,
                grep=grep,
                index=index),
            header=header, footer=footer, exit=exit, )
