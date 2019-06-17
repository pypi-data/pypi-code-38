# -*- coding: utf-8 -*-
"""
Clean up configparser cfg files:
-remove extra whitespace
-sort sections by headers
-sort variable defs by variable, keeping comment lines for each var
-properly indent list and dict type variables

@author: Jussi (jnu@iki.fi)
"""

from __future__ import print_function
import re



def is_comment(s):
    """Match line comment starting with # or ;"""
    p = re.compile(r'[\s]*[#;].*')
    return bool(p.match(s))        


def is_var_def(s):
    """Match var definition"""
    p = re.compile(r'[\s]*[\S]+[\s]*=[\s]*[\S]+[\s]*')
    return bool(p.match(s))


def is_list_def(s):
    """Match list or dict definition"""
    p = re.compile(r'[\s]*[\S]+[\s]*=[\s]*[\[,\{][\S]+[\s]*')
    return bool(p.match(s))


def is_section_header(s):
    """Match section headers of form [string]"""
    p = re.compile(r'^\[[\w]*\]$')
    return bool(p.match(s))


def not_whitespace(s):
    """Non-whitespace line, should be a continuation of definition"""
    p = re.compile(r'[\s]*[\S]+')  # match whitespace-only lines
    return bool(p.match(s))



def parse_cfg(lines):
    """Parse cfg lines into dict"""
    var_comments = list()
    di = dict()
    var = None
    for n, li in enumerate(lines):
        if is_section_header(li):
            this_section = li
            di[this_section] = dict()
        elif is_comment(li):
            var_comments.append(li)
        elif is_var_def(li):
            var = li.split('=')[0].strip()
            di[this_section][var] = dict()
            di[this_section][var]['comments'] = var_comments
            di[this_section][var]['def_lines'] = list()
            di[this_section][var]['def_lines'].append(li)
            var_comments = list()
            # figure out indentation for list-type defs
            if is_list_def(li):
                idnt = max(li.find('['), li.find('{'))
        elif not_whitespace(li):  # continuation line
            if var is not None and var in di[this_section]:
                if idnt is not None and idnt > 0:  # indent also def continuation lines
                    li = (idnt + 1) * ' ' + li.strip()
                di[this_section][var]['def_lines'].append(li)
            else:  # orphan non-whitespace line
                raise ValueError('Parse error at line %d: %s' % (n, li))
    return di


def clean_print(di):
    """Nicely output a dict parsed by parse_cfg"""
    for sect in sorted(di.keys()):
        yield ''
        yield sect
        # whether section has var definitions spanning multiple lines
        has_multiline_defs = any(len(di[sect][var]['def_lines']) > 1
                                 for var in di[sect])
        for var in sorted(di[sect].keys()):
            # print comments and definition for this var
            if di[sect][var]['comments']:
                yield '\n'.join(di[sect][var]['comments'])
            def_this = di[sect][var]['def_lines']
            yield '\n'.join(def_this)
            # output extra whitespace for sections that have multiline defs
            if has_multiline_defs:
                yield ''
            
        