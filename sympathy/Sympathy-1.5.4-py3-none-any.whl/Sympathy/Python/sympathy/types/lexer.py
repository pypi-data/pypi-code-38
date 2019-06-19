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
import ply.lex as lex
import os
# Force preload of lexer and parser to avoid warning and regeneration by ply.
try:
    from . import types_lexer as _types_lexer  # NOQA
except ImportError:
    _types_lexer = 'types_lexer'

_outputdir = os.path.dirname(os.path.abspath(__file__))

precedence = ()

reserved = {'sytypealias': 'ALIAS',
            'sytext': 'TEXT',
            'sytable': 'TABLE'}

rreserved = dict(zip(reserved.values(), reserved.keys()))

tokens = ['EOL',
          'EQUALS',
          'LPAREN',
          'RPAREN',
          'COLON',
          'LBRACKET',
          'RBRACKET',
          'LABRACKET',
          'RABRACKET',
          'LBRACE',
          'RBRACE',
          'COMMA',
          'ARROW']

tokens.extend(reserved.values())
tokens.append('IDENTIFIER')

t_ignore = r' '
t_EOL = r'[\n\r]+'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LABRACKET = r'<'
t_RABRACKET = r'>'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COLON = r':'
t_COMMA = r','
t_ARROW = '->'


def t_IDENTIFIER(token):
    r'[A-Za-z][A-Za-z0-9-_]*'
    token.type = reserved.get(token.value, 'IDENTIFIER')
    return token


# Error handling rule
def t_error(token):
    raise TypeError('Illegal character {} at position {} in {}'.format(
        token.value[0], token.lexpos,
        token.lexer.lexdata.strip()))


lexer = lex.lex(debug=0,
                optimize=1,
                lextab=_types_lexer,
                outputdir=_outputdir)
