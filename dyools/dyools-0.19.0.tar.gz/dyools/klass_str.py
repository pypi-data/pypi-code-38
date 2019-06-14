from __future__ import (absolute_import, division, print_function, unicode_literals)

import itertools
import unicodedata


class Str(object):
    def __init__(self, arg, numeric=False, precision=2, prefix=False, suffix=False):
        self.arg = '{}'.format(arg)
        self.numeric = any([numeric, isinstance(arg, (int, float))])
        self.precision = precision
        self.prefix = prefix
        self.suffix = suffix

    def to_code(self):
        txt = self.arg.strip()
        txt = [x for x in txt if x.isalnum() or x == ' ']
        txt = ''.join(txt)
        txt = '_'.join(txt.strip().upper().split())
        txt = [c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn']
        txt = ''.join(txt)
        return self.to_str(txt)

    def dot_to_underscore(self):
        """
        Replace all dots to underscores in the Str Object
        :return: String
        """
        txt = self.arg.strip().replace('.', '_')
        return self.to_str(txt)

    def to_title(self):
        """
        Split the string in the Str Object to a list using the separator ['-', '*', '.', '_'] and then capitalize each one
        :return: String
        """
        txt = self.arg.strip()
        txt = Str(txt).replace({' ': ['-', '*', '.', '_']})
        txt = txt.split()
        txt = [x.title() for x in txt if x]
        txt = ' '.join(txt)
        return self.to_str(txt)

    def remove_spaces(self):
        """
        Remove spaces from the Str Object
        :return: String
        """
        res = self.arg.replace(' ', '')
        return self.to_str(res)

    def replace(self, kwargs):
        arg = self.arg
        for key, values in kwargs.items():
            if not isinstance(values, (list, tuple)):
                values = [values]
            for v in values:
                arg = arg.replace(v, key)
        res = '{}'.format(arg)
        return self.to_str(res)

    def with_separator(self, sep=' ', nbr=3, rtl=True):
        step = -1 if rtl else 1
        precision = None
        arg = self.arg
        if self.numeric and '.' in self.arg:
            arg, precision = self.arg.split('.', 2)
            precision = precision[:self.precision]
            precision = '{:0<{p}}'.format(precision, p=self.precision)
        arg = arg[::step]
        res = '{}'.format('')
        while arg:
            if res:
                res += '{}'.format(sep)
            res += '{}'.format(arg[:nbr])
            arg = arg[nbr:]
        res = res[::step]
        if not precision is None:
            res = '{}.{}'.format(res, precision)
        return self.to_str(res)

    def case_combinations(self):
        str1 = [x.lower() for x in self.arg]
        str2 = [x.upper() for x in self.arg]
        combination = list(set((list(itertools.product(*zip(str1, str2))))))
        return [''.join(x) for x in combination]

    def remove_accents(self):
        txt = self.arg
        txt = [c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn']
        txt = ''.join(txt)
        return self.to_str(txt)

    def to_number(self, ttype=float):
        txt = self.arg.strip().replace(',', '.')
        txt = [c for c in txt if c.isdigit() or c == '.']
        txt = ''.join(txt)
        return ttype(float(txt))

    def get_first_number(self, ttype=float):
        txt = self.arg.strip().replace(',', '.')
        tmp = ''
        for c in txt:
            if c.isdigit() or c == '.':
                tmp += c
            elif tmp:
                break
        return ttype(tmp)

    def get_last_number(self, ttype=float):
        txt = self.arg[::-1].strip().replace(',', '.')
        tmp = ''
        for c in txt:
            if c.isdigit() or c == '.':
                tmp += c
            elif tmp:
                break
        return ttype(tmp[::-1])

    def to_range(self, ttype=float, or_equal=False, separators='-', min_number=0, max_number=99999):
        txt = self.arg.strip()
        if not isinstance(separators, (list, tuple)):
            separators = [separators]
        for sep in separators:
            txt = txt.replace(sep, '-')
        step = 1 if ttype == int else 0.01
        if or_equal:
            step = 0
        min_, max_ = min_number, max_number
        if '>=' in txt:
            splitted = txt.split('>=')
            if len(splitted) > 1:
                min_ = Str(splitted[-1]).to_number(ttype=ttype)
        elif '>' in txt:
            splitted = txt.split('>')
            if len(splitted) > 1:
                min_ = Str(splitted[-1]).to_number(ttype=ttype) + step
        elif '<=' in txt:
            splitted = txt.split('<=')
            if len(splitted) > 1:
                max_ = Str(splitted[-1]).to_number(ttype=ttype)
        elif '<' in txt:
            splitted = txt.split('<')
            if len(splitted) > 1:
                max_ = Str(splitted[-1]).to_number(ttype=ttype) - step
        elif '-' in txt:
            splitted = txt.split('-')
            if len(splitted) > 1:
                min_ = Str(splitted[0]).to_number(ttype=ttype)
                max_ = Str(splitted[-1]).to_number(ttype=ttype)
        elif txt:
            min_ = max_ = Str(txt).to_number(ttype=ttype)
        if min_ > max_:
            return max_, min_
        else:
            return min_, max_

    def to_str(self, arg=None):
        if arg is None:
            arg = self.arg
        fmt = '{value}'
        if self.prefix:
            fmt = '{prefix} ' + fmt
        if self.suffix:
            fmt += ' {suffix}'
        return fmt.format(value=arg, prefix=self.prefix, suffix=self.suffix)

    def is_equal(self, arg):
        arg = '{}'.format(arg)
        clean = lambda s: s.replace(' ', '').strip().lower()
        return clean(arg) == clean(self.arg)

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return self.to_str()
