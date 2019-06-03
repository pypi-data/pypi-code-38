from __future__ import absolute_import
from __future__ import print_function
__author__ = "Sapan Bhatia"

__copyright__ = "Copyright (C) 2017 Open Networking Lab"
__version__ = "1.0"

import sys
from .helpers import LexHelper


class FOLParsingError(Exception):

    def __init__(self, message, error_range):
        super(FOLParsingError, self).__init__(message)
        self.error_range = error_range


class FOLLexer(object):
    keywords = ('forall', 'exists', 'True', 'False', 'not', 'in')

    tokens = ['STRING_LITERAL',
              'NUM',
              'ESCAPE',
              'COLON',
              'IMPLIES',
              'OR',
              'AND',
              'LPAREN',
              'RPAREN',
              'EQUALS',
              'SYMBOL',
              'LT',
              'RT',
              'STAR'] + [k.upper() for k in keywords]
    # literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_ignore_LINE_COMMENT = '//.*'
    t_COLON = '\\:'
    t_IMPLIES = '\\-\\>'
    t_OR = '\\|'
    t_STAR = '\\*'
    t_LT = '\\<'
    t_RT = '\\>'
    t_AND = '\\&'
    t_LPAREN = '\\('
    t_RPAREN = '\\)'
    t_NUM = r'[+-]?\d+(\.\d+)?'
    t_STRING_LITERAL = r'\"([^\\\n]|(\\.))*?\"'

    t_EQUALS = '\\='

    literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_ignore = ' \t\f'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_newline2(self, t):
        r'(\r\n)+'
        t.lexer.lineno += len(t.value) / 2

    def t_ESCAPE(self, t):
        r'{{ (.|\n)*? }}'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_BLOCK_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    def t_SYMBOL(self, t):
        r'[A-Za-z_$][\.A-Za-z0-9_+$]*(\(\))?'
        if t.value in FOLLexer.keywords:
            t.type = t.value.upper()
        return t

    def t_error(self, t):
        print(("Illegal character '{}' ({}) in line {}".format(
            t.value[0], hex(ord(t.value[0])), t.lexer.lineno)),
            file=sys.stderr)
        t.lexer.skip(1)


class FOLParser(object):
    tokens = FOLLexer.tokens
    offset = 0
    lh = LexHelper()

    def setOffset(self, of):
        self.offset = of
        self.lh.offset = of

    def p_term_numeric_constant(self, p):
        '''term : NUM'''
        p[0] = p[1]

    def p_term_string_constant(self, p):
        '''term : STRING_LITERAL'''
        p[0] = p[1]

    def p_term_boolean_constant(self, p):
        '''term :   FALSE
                    | TRUE'''
        p[0] = p[1]

    def p_term_policy_function(self, p):
        '''term : STAR SYMBOL LPAREN SYMBOL RPAREN'''
        p[0] = {'policy': [p[2], p[4]]}

    def p_fole_not(self, p):
        '''fole : NOT fole'''
        p[0] = {p[1]: p[2]}

    def p_fole_term(self, p):
        '''fole : term'''
        p[0] = p[1]

    def p_term_symbol(self, p):
        '''term : SYMBOL'''
        p[0] = p[1]

    def p_term_python(self, p):
        '''term : ESCAPE'''
        p[0] = {'python': p[1].lstrip('{ ').rstrip(' }')}

    def p_fole_group(self, p):
        "fole : LPAREN fole RPAREN"
        p[0] = p[2]

    def p_fole_in(self, p):
        "fole : term IN term"
        p[0] = {'in': (p[1], p[3])}

    def p_fole_equals(self, p):
        "fole : term EQUALS term"
        p[0] = {'=': (p[1], p[3])}

    def p_fole_binary(self, p):
        '''fole : fole AND fole
                  | fole OR fole
                  | fole IMPLIES fole'''
        p[0] = {p[2]: [p[1], p[3]]}

    def p_fole_quant(self, p):
        '''fole :     FORALL SYMBOL COLON fole
                      | EXISTS SYMBOL COLON fole'''
        p[0] = {p[1]: [p[2], p[4]]}

    def p_goal(self, p):
        '''goal : LT fole RT'''
        p[0] = p[2]

    def p_error(self, p):
        error = 'error: {}'.format(p)
        raise FOLParsingError(error, (p.lineno, p.lexpos, len(p.value)))

    precedence = (
        ("right", "IMPLIES"),
        ("left", "OR"),
        ("left", "AND"),
        ("right", "COLON"),
        ("right", "NOT"),
        ("right", "STAR"),
        ("right", "ESCAPE"),
        ("nonassoc", "EQUALS", "IN"))
