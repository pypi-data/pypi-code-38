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
"""Parser for ASAM ATF using ply"""

from ply import yacc
from . lexer import (tokens, COMMA, SEMICOLON)
from . lexer import lexer as atflex


def p_atffile(p):
    'atffile : ATF_FILE VERSION SEMICOLON texp ATF_END SEMICOLON'
    p[0] = ((p[1], p[2]), p[4])


# 'DT_BLOB'
def p_datatype_blob(p):
    """
    datatype : DT_BLOB
             | DT_BOOLEAN
             | DT_BYTE
             | DT_BYTESTR
             | DT_COMPLEX
             | DT_DATE
             | DT_DCOMPLEX
             | DT_DOUBLE
             | DT_ENUM
             | DT_EXTERNALREFERENCE
             | DT_LONG
             | DT_LONGLONG
             | DT_FLOAT
             | DT_SHORT
             | DT_STRING
             | DT_UNKNOWN
             | DS_STRING
    """
    p[0] = p[1]


def p_dexp_datatype(p):
    'dexp : DATATYPE datatype'
    p[0] = p[2]


# 'FILES'
def p_files(p):
    'files : FILES filedefs ENDFILES'
    p[0] = {'files': dict(p[2])}


def p_filedef(p):
    'filedefs : COMPONENT IDENTIFIER ASSIGN STRING SEMICOLON'
    p[0] = [(p[2], p[4])]


def p_filedefs_combine(p):
    'filedefs : filedefs filedefs'
    p[0] = p[1] + p[2]


def p_include(p):
    """
    include : INCLUDE IDENTIFIER
            | include COMMA IDENTIFIER
    """
    if p[2] == COMMA:
        p[1].append(p[3])
    else:
        p[0] = [p[2]]


# 'APPLELEM'
def p_applelem(p):
    'applelem : APPLELEM IDENTIFIER COMMA BASETYPE IDENTIFIER applattr ENDAPPLELEM'
    p[0] = {'applelem': {p[2]: (p[2], p[5], p[6])}}


def p_cardinality(p):
    """
    cardinality : INTEGER COMMA INTEGER
                | INTEGER COMMA MANY
    """
    p[0] = [p[1], p[3]]


def p_idattr(p):
    """
    idattr : BASETYPE
           | BASEATTR
           | REF_TO
           | REF_TYPE
    """
    p[0] = p[1]


def p_attr(p):
    """
    attr : CARDINALITY cardinality
         | DATATYPE datatype
         | idattr IDENTIFIER
    """
    p[0] = {p[1]: p[2]}


def p_attrs(p):
    """
    attrs : attr
          | attrs COMMA attr
    """
    if len(p) > 2:
        p[1].update(p[3])
    p[0] = p[1]


# 'APPLATTR'
def p_applattr_base(p):
    'applattr : APPLATTR IDENTIFIER COMMA attrs'
    p[4][p[1]] = p[2]
    p[0] = {p[2]: p[4]}


# 'APPLATTR'
def p_applattr_combine(p):
    """
    applattr : applattr applattr
             | applattr SEMICOLON
    """
    if p[2] == SEMICOLON:
        p[0] = p[1]
    else:
        p[0] = dict(p[1], **p[2])


# 'INSTELEM'
def p_instelem(p):
    'instelem : INSTELEM IDENTIFIER attribute_values ENDINSTELEM'
    attribute_dict = dict(p[3])
    p[0] = {'instelem': {p[2]: {attribute_dict['Id']: attribute_dict}}}


def p_attribute_values_single(p):
    'attribute_values : IDENTIFIER ASSIGN data_attribute_values'
    p[0] = [(p[1], p[3])]


def p_attribute_values_combine(p):
    'attribute_values : attribute_values attribute_values'
    p[1].extend(p[2])
    p[0] = p[1]


def p_data_attribute_values_dexp(p):
    'data_attribute_values : dexp COMMA dval'
    p[0] = (p[1], p[3])


def p_data_attribute_values(p):
    'data_attribute_values : dval'
    p[0] = p[1]


def p_dval_prims(p):
    """
    dval : prim SEMICOLON
         | prims SEMICOLON
    """
    p[0] = p[1]


def p_val_comp_num_type(p):
    """
    comp_num_type : DT_BOOLEAN
                  | DT_BYTE
                  | DT_SHORT
                  | DT_LONG
                  | DT_LONGLONG
                  | DT_FLOAT
                  | IEEEFLOAT4
                  | IEEEFLOAT8
    """
    p[0] = p[1]


def p_val_comp_str_type(p):
    """
    comp_str_type : DT_STRING
                  | DT_BYTESTR
    """
    p[0] = p[1]


def p_val_comp_blob(p):
    'comp_blob : DT_BLOB INTEGER COMMA DESCRIPTION STRING'
    p[0] = {'TYPE': p[1], 'LENGTH': p[2], p[4]: p[5]}


def p_val_comp_num(p):
    'comp_num : comp_num_type INTEGER COMMA \
                INIOFFSET INTEGER COMMA \
                BLOCKSIZE INTEGER COMMA \
                VALPERBLOCK INTEGER COMMA \
                VALOFFSETS ints'
    p[0] = {
        'TYPE': p[1],
        'LENGTH': p[2],
        p[4]: p[5],
        p[7]: p[8],
        p[10]: p[11],
        p[13]: p[14]}


def p_val_comp_str(p):
    'comp_str : comp_str_type INTEGER COMMA INIOFFSET INTEGER'
    p[0] = {'TYPE': p[1], 'LENGTH': p[2], p[4]: p[5]}


def p_val_comp(p):
    """
    comp : comp_blob
         | comp_num
         | comp_str
    """
    p[0] = p[1]


def p_dval_component(p):
    'dval : COMPONENT IDENTIFIER COMMA comp ENDCOMPONENT SEMICOLON'
    p[4][p[1]] = p[2]
    p[0] = p[4]


def p_dval_undefined(p):
    'dval : UNDEFINED SEMICOLON'
    p[0] = None


def p_ints(p):
    """
    ints : INTEGER
         | ints COMMA INTEGER
    """
    if len(p) > 2:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]


def p_prim(p):
    """
    prim : BOOL
         | FLOAT
         | INTEGER
         | STRING
    """
    p[0] = p[1]


def p_prims1(p):
    'prims : prim COMMA prim'
    p[0] = [p[1], p[3]]


def p_prims2(p):
    'prims : prims COMMA prim'
    p[1].append(p[3])
    p[0] = p[1]


def dictadd(dicta, dictb):
    """
    Add two dictionaries,
    assuming that the second dictionary contains only only one element.
    """
    for key in dictb:
        if key in dicta:
            nextlevel = dicta[key]
            if isinstance(nextlevel, dict):
                dictadd(nextlevel, dictb[key])
        else:
            dicta.update(dictb)


def p_texp_combine(p):
    'texp : texp tsexp SEMICOLON'
    dictadd(p[1], p[2])
    p[0] = p[1]


def p_texp_tsexp(p):
    'texp : tsexp SEMICOLON'
    p[0] = p[1]


def p_tsexp_files(p):
    """
    tsexp : files
          | include
          | applelem
          | instelem
    """
    p[0] = p[1]


def p_error(p):
    """Error rule for syntax errors"""
    print('Syntax error at input! {0}'.format(str(p)))


_stringparser = yacc.yacc(
    debug=0, optimize=1, write_tables=0)


def fileparser(filename):
    with open(filename) as f:
        return stringparser(f.read())


def stringparser(string):
    return _stringparser.parse(string, lexer=atflex)
