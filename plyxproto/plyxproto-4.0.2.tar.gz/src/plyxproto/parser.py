from __future__ import absolute_import
from __future__ import print_function

__author__ = "Dusan (Ph4r05) Klinec, Sapan Bhatia, ONF"
__copyright__ = "Copyright (C) 2014 Dusan (ph4r05) Klinec, 2017-2019 ONF"
__license__ = "Apache License, Version 2.0"

import ply.lex as lex
import ply.yacc as yacc

from .model import (
    DotName,
    EnumDefinition,
    EnumFieldDefinition,
    ExtensionsDirective,
    ExtensionsMax,
    FieldDefinition,
    FieldDirective,
    FieldType,
    ImportStatement,
    LinkDefinition,
    LinkSpec,
    Literal,
    MapDefinition,
    MessageDefinition,
    MessageExtension,
    MethodDefinition,
    Name,
    OptionStatement,
    PackageStatement,
    PolicyDefinition,
    ProtoFile,
    ReduceDefinition,
    ServiceDefinition,
)

from .helpers import LexHelper, LU
from .logicparser import FOLParser, FOLLexer, FOLParsingError
import ast
import sys


class PythonError(Exception):
    pass


class ParsingError(Exception):

    def __init__(self, message, error_range):
        super(ParsingError, self).__init__(message)
        self.error_range = error_range


class ProtobufLexer(object):
    keywords = (
        'double',
        'float',
        'int32',
        'int64',
        'uint32',
        'uint64',
        'sint32',
        'sint64',
        'fixed32',
        'fixed64',
        'sfixed32',
        'sfixed64',
        'bool',
        'string',
        'bytes',
        'message',
        'required',
        'optional',
        'repeated',
        'enum',
        'extensions',
        'max',
        'extend',
        'to',
        'package',
        '_service',
        'rpc',
        'returns',
        'true',
        'false',
        'option',
        'import',
        'manytoone',
        'manytomany',
        'onetoone',
        'policy',
        'map',
        'reduce')

    tokens = [
        'POLICYBODY',
        'NAME',
        'NUM',
        'STRING_LITERAL',
        # 'LINE_COMMENT', 'BLOCK_COMMENT',
        'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK',
        'LPAR', 'RPAR', 'EQ', 'SEMI', 'DOT',
        'ARROW', 'COLON', 'COMMA', 'SLASH',
        'DOUBLECOLON',
        'STARTTOKEN'
    ] + [k.upper() for k in keywords]

    def t_POLICYBODY(self, t):
        r'< (.|\n)*? [^-]>'
        t.lexer.lineno += t.value.count('\n')
        return t

    literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_NUM = r'[+-]?\d+(\.\d+)?'
    t_STRING_LITERAL = r'\"([^\\\n]|(\\.))*?\"'

    t_ignore_LINE_COMMENT = '//.*'

    def t_BLOCK_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    t_LBRACE = '{'
    t_RBRACE = '}'
    t_LBRACK = '\\['
    t_RBRACK = '\\]'

    t_LPAR = '\\('
    t_RPAR = '\\)'
    t_EQ = '='
    t_SEMI = ';'
    t_ARROW = '\\-\\>'
    t_COLON = '\\:'
    t_SLASH = '\\/'
    t_COMMA = '\\,'
    t_DOT = '\\.'
    t_ignore = ' \t\f'
    t_STARTTOKEN = '\\+'
    t_DOUBLECOLON = '\\:\\:'

    def t_NAME(self, t):
        '[A-Za-z_$][A-Za-z0-9_+$]*'
        if t.value in ProtobufLexer.keywords:
            # print "type: %s val %s t %s" % (t.type, t.value, t)
            t.type = t.value.upper()
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_newline2(self, t):
        r'(\r\n)+'
        t.lexer.lineno += len(t.value) / 2

    def t_error(self, t):
        print(("Illegal character '{}' ({}) in line {}".format(
            t.value[0], hex(ord(t.value[0])), t.lexer.lineno)),
            file=sys.stderr)
        t.lexer.skip(1)


def srcPort(x):
    if (x):
        return [FieldDirective(Name('port'), x)]
    else:
        return []


class ProtobufParser(object):
    tokens = ProtobufLexer.tokens
    offset = 0
    lh = LexHelper()
    fol_lexer = lex.lex(module=FOLLexer())  # , optimize=1)
    fol_parser = yacc.yacc(
        module=FOLParser(),
        start='goal',
        outputdir='/tmp',
        debug=0)

    def setOffset(self, of):
        self.offset = of
        self.lh.offset = of

    def p_empty(self, p):
        '''empty :'''
        pass

    def p_field_modifier(self, p):
        '''field_modifier : REQUIRED
                          | OPTIONAL
                          | REPEATED'''
        p[0] = LU.i(p, 1)

    def p_primitive_type(self, p):
        '''primitive_type : DOUBLE
                          | FLOAT
                          | INT32
                          | INT64
                          | UINT32
                          | UINT64
                          | SINT32
                          | SINT64
                          | FIXED32
                          | FIXED64
                          | SFIXED32
                          | SFIXED64
                          | BOOL
                          | STRING
                          | BYTES'''
        p[0] = LU.i(p, 1)

    def p_link_type(self, p):
        '''link_type      : ONETOONE
                          | MANYTOONE
                          | MANYTOMANY'''
        p[0] = LU.i(p, 1)

    def p_field_id(self, p):
        '''field_id : NUM'''
        p[0] = LU.i(p, 1)

    def p_reverse_id(self, p):
        '''reverse_id : NUM'''
        p[0] = LU.i(p, 1)

    def p_rvalue(self, p):
        '''rvalue : NUM
                  | TRUE
                  | FALSE'''
        p[0] = LU.i(p, 1)

    def p_rvalue3(self, p):
        '''rvalue : STRING_LITERAL'''
        p[0] = Name(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)
        p[0].deriveLex()

    def p_rvalue2(self, p):
        '''rvalue : NAME'''
        p[0] = Name(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)
        p[0].deriveLex()

    def p_field_directives2(self, p):
        '''field_directives : empty'''
        p[0] = []

    def p_field_directives(self, p):
        '''field_directives : LBRACK field_directive_times RBRACK'''
        p[0] = p[2]
        # self.lh.set_parse_object(p[0], p)

    def p_field_directive(self, p):
        '''field_directive : NAME EQ rvalue'''
        p[0] = FieldDirective(Name(LU.i(p, 1)), LU.i(p, 3))
        self.lh.set_parse_object(p[0], p)

    def p_policy_opt_explicit(self, p):
        '''policy_opt : DOUBLECOLON NAME'''
        p[0] = p[2]

    def p_policy_opt_empty(self, p):
        '''policy_opt : empty'''
        p[0] = None

    def p_csv_expr(self, p):
        '''csv_expr : LPAR csv RPAR'''
        p[0] = p[2]

    def p_csv_expr2(self, p):
        '''csv_expr : empty'''
        p[0] = []

    def p_csv2(self, p):
        '''csv : empty'''

    def p_csv(self, p):
        '''csv : dotname
               | csv COMMA dotname'''

        if len(p) == 2:
            p[0] = [LU(p, 1)]
        else:
            p[0] = p[1] + [LU(p, 3)]

    def p_field_directive_times(self, p):
        '''field_directive_times : field_directive_plus'''
        p[0] = p[1]

    def p_field_directive_times2(self, p):
        '''field_directive_times : empty'''
        p[0] = []

    def p_field_directive_plus(self, p):
        '''field_directive_plus : field_directive
                               | field_directive_plus COMMA field_directive'''
        if len(p) == 2:
            p[0] = [LU(p, 1)]
        else:
            p[0] = p[1] + [LU(p, 3)]

    def p_dotname(self, p):
        '''dotname : NAME
                   | dotname DOT NAME'''
        if len(p) == 2:
            p[0] = [LU(p, 1)]
        else:
            p[0] = p[1] + [LU(p, 3)]

    # Hack for cases when there is a field named 'message' or 'max'
    def p_fieldName(self, p):
        '''field_name : STARTTOKEN
                      | NAME
                      | MESSAGE
                      | MAX'''
        p[0] = Name(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)
        p[0].deriveLex()

    def p_field_type(self, p):
        '''field_type : primitive_type'''
        p[0] = FieldType(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)

    def p_field_type2(self, p):
        '''field_type : dotname'''
        p[0] = DotName(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)
        p[0].deriveLex()

    def p_slash_name(self, p):
        '''slash_name : SLASH dotname'''
        p[0] = p[2]
        # self.lh.set_parse_object(p[0], p)

    def p_slash_name2(self, p):
        '''slash_name : empty'''
        p[0] = None

    def p_colon_fieldname(self, p):
        '''colon_fieldname : COLON field_name'''
        p[0] = p[2]
        self.lh.set_parse_object(p[0], p)

    def p_colon_fieldname2(self, p):
        '''colon_fieldname : empty'''
        p[0] = None

    # TODO: Add directives to link definition
    def p_link_definition(self, p):
        '''
        link_definition : field_modifier link_type field_name policy_opt ARROW dotname slash_name colon_fieldname EQ field_id field_directives SEMI
        '''

        p[0] = LinkSpec(
            FieldDefinition(
                LU.i(
                    p, 1), Name('int32'), LU.i(
                    p, 3), LU.i(
                    p, 4), LU.i(
                        p, 10), [
                            FieldDirective(
                                Name('type'), Name('link')), FieldDirective(
                                    Name('model'), LU.i(
                                        p, 6))] + srcPort(
                                            LU.i(
                                                p, 8)) + LU.i(
                                                    p, 11)), LinkDefinition(
                                                        LU.i(
                                                            p, 2), LU.i(
                                                                p, 3), LU.i(
                                                                    p, 6), LU.i(
                                                                        p, 7), LU.i(
                                                                            p, 8)))

        self.lh.set_parse_object(p[0], p)

    # TODO: Add directives to link definition
    def p_link_definition_with_reverse(self, p):
        '''
        link_definition_with_reverse : field_modifier link_type field_name policy_opt ARROW dotname slash_name colon_fieldname EQ field_id COLON reverse_id field_directives SEMI
        '''
        p[0] = LinkSpec(
            FieldDefinition(
                LU.i(
                    p, 1), Name('int32'), LU.i(
                    p, 3), LU.i(
                    p, 4), LU.i(
                        p, 10), [
                            FieldDirective(
                                Name('type'), Name('link')), FieldDirective(
                                    Name('model'), LU.i(
                                        p, 6))] + srcPort(
                                            LU.i(
                                                p, 8)) + LU.i(
                                                    p, 13)), LinkDefinition(
                                                        LU.i(
                                                            p, 2), LU.i(
                                                                p, 3), LU.i(
                                                                    p, 6), LU.i(
                                                                        p, 7), LU.i(
                                                                            p, 8), reverse_id=LU.i(p, 12)))

        self.lh.set_parse_object(p[0], p)

    # Root of the field declaration.
    def p_field_definition(self, p):
        '''field_definition : field_modifier field_type field_name policy_opt EQ field_id field_directives SEMI'''
        p[0] = FieldDefinition(
            LU.i(
                p, 1), LU.i(
                p, 2), LU.i(
                p, 3), LU.i(
                    p, 4), LU.i(
                        p, 6), LU.i(
                            p, 7))
        self.lh.set_parse_object(p[0], p)

    # Root of the enum field declaration.
    def p_enum_field(self, p):
        '''enum_field : field_name EQ NUM SEMI'''
        p[0] = EnumFieldDefinition(LU.i(p, 1), LU.i(p, 3))
        self.lh.set_parse_object(p[0], p)

    def p_enum_body_part(self, p):
        '''enum_body_part : enum_field
                          | option_directive'''
        p[0] = p[1]

    def p_enum_body(self, p):
        '''enum_body : enum_body_part
                    | enum_body enum_body_part'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_enum_body_opt(self, p):
        '''enum_body_opt : empty'''
        p[0] = []

    def p_enum_body_opt2(self, p):
        '''enum_body_opt : enum_body'''
        p[0] = p[1]

    def p_reduce_definition(self, p):
        '''reduce_definition : REDUCE NAME POLICYBODY'''
        ltxt = p[3].lstrip('<').rstrip('>')
        al = ast.parse(ltxt).body[0]
        if not isinstance(al, ast.Expr):
            raise PythonError("reduce operator needs to be an expression")
        elif not isinstance(al.value, ast.Lambda):
            raise PythonError("reduce operator needs to be a lambda")

        p[0] = ReduceDefinition(Name(LU.i(p, 2)), ltxt)
        self.lh.set_parse_object(p[0], p)

    def p_map_definition(self, p):
        '''map_definition : MAP NAME POLICYBODY'''
        ltxt = p[3].lstrip('<').rstrip('>')
        al = ast.parse(ltxt).body[0]
        if not isinstance(al, ast.Expr):
            raise PythonError("map operator needs to be an expression")
        elif not isinstance(al.value, ast.Lambda):
            raise PythonError("map operator needs to be a lambda")

        p[0] = MapDefinition(Name(LU.i(p, 2)), ltxt)
        self.lh.set_parse_object(p[0], p)

    def p_policy_definition(self, p):
        '''policy_definition : POLICY NAME POLICYBODY'''
        try:
            fol = self.fol_parser.parse(p[3], lexer=self.fol_lexer)
        except FOLParsingError as e:
            lineno, lexpos, length = e.error_range
            raise ParsingError(
                "Policy parsing error in policy %s" %
                p[2], (p.lineno(3) + lineno, lexpos + p.lexpos(3), length))
        p[0] = PolicyDefinition(Name(LU.i(p, 2)), fol)
        self.lh.set_parse_object(p[0], p)

    # Root of the enum declaration.
    # enum_definition ::= 'enum' ident '{' { ident '=' integer ';' }* '}'
    def p_enum_definition(self, p):
        '''enum_definition : ENUM NAME LBRACE enum_body_opt RBRACE'''
        p[0] = EnumDefinition(Name(LU.i(p, 2)), LU.i(p, 4))
        self.lh.set_parse_object(p[0], p)

    def p_extensions_to(self, p):
        '''extensions_to : MAX'''
        p[0] = ExtensionsMax()
        self.lh.set_parse_object(p[0], p)

    def p_extensions_to2(self, p):
        '''extensions_to : NUM'''
        p[0] = LU.i(p, 1)

    # extensions_definition ::= 'extensions' integer 'to' integer ';'
    def p_extensions_definition(self, p):
        '''extensions_definition : EXTENSIONS NUM TO extensions_to SEMI'''
        p[0] = ExtensionsDirective(LU.i(p, 2), LU.i(p, 4))
        self.lh.set_parse_object(p[0], p)

    # message_extension ::= 'extend' ident '{' message_body '}'
    def p_message_extension(self, p):
        '''message_extension : EXTEND NAME LBRACE message_body RBRACE'''
        p[0] = MessageExtension(Name(LU.i(p, 2)), LU.i(p, 4))
        self.lh.set_parse_object(p[0], p)

    def p_message_body_part(self, p):
        '''message_body_part : field_definition
                           | link_definition
                           | link_definition_with_reverse
                           | enum_definition
                           | option_directive
                           | message_definition
                           | extensions_definition
                           | message_extension'''
        p[0] = p[1]

    # message_body ::= { field_definition | enum_definition |
    # message_definition | extensions_definition | message_extension }*
    def p_message_body(self, p):
        '''message_body : empty'''
        p[0] = []

    # message_body ::= { field_definition | enum_definition |
    # message_definition | extensions_definition | message_extension }*
    def p_message_body2(self, p):
        '''message_body : message_body_part
                      | message_body message_body_part'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    # Root of the message declaration.
    # message_definition = MESSAGE_ - ident("messageId") + LBRACE + message_body("body") + RBRACE
    def p_message_definition(self, p):
        '''message_definition : MESSAGE NAME policy_opt csv_expr LBRACE message_body RBRACE'''
        p[0] = MessageDefinition(
            Name(
                LU.i(
                    p, 2)), LU.i(
                p, 3), LU.i(
                    p, 4), LU.i(
                        p, 6))
        self.lh.set_parse_object(p[0], p)

    # method_definition ::= 'rpc' ident '(' [ ident ] ')' 'returns' '(' [
    # ident ] ')' ';'
    def p_method_definition(self, p):
        '''method_definition : RPC NAME LPAR NAME RPAR RETURNS LPAR NAME RPAR'''
        p[0] = MethodDefinition(
            Name(
                LU.i(
                    p, 2)), Name(
                LU.i(
                    p, 4)), Name(
                        LU.i(
                            p, 8)))
        self.lh.set_parse_object(p[0], p)

    def p_method_definition_opt(self, p):
        '''method_definition_opt : empty'''
        p[0] = []

    def p_method_definition_opt2(self, p):
        '''method_definition_opt : method_definition
                          | method_definition_opt method_definition'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    # service_definition ::= 'service' ident '{' method_definition* '}'
    # service_definition = SERVICE_ - ident("serviceName") + LBRACE + ZeroOrMore(Group(method_definition)) + RBRACE
    def p_service_definition(self, p):
        '''service_definition : _SERVICE NAME LBRACE method_definition_opt RBRACE'''
        p[0] = ServiceDefinition(Name(LU.i(p, 2)), LU.i(p, 4))
        self.lh.set_parse_object(p[0], p)

    # package_directive ::= 'package' ident [ '.' ident]* ';'
    def p_package_directive(self, p):
        '''package_directive : PACKAGE dotname SEMI'''
        p[0] = PackageStatement(Name(LU.i(p, 2)))
        self.lh.set_parse_object(p[0], p)

    # import_directive = IMPORT_ - quotedString("importFileSpec") + SEMI
    def p_import_directive(self, p):
        '''import_directive : IMPORT STRING_LITERAL SEMI'''
        p[0] = ImportStatement(Literal(LU.i(p, 2)))
        self.lh.set_parse_object(p[0], p)

    def p_option_rvalue(self, p):
        '''option_rvalue : NUM
                         | TRUE
                         | FALSE'''
        p[0] = LU(p, 1)

    def p_option_rvalue2(self, p):
        '''option_rvalue : STRING_LITERAL'''
        p[0] = Literal(LU(p, 1))

    def p_option_rvalue3(self, p):
        '''option_rvalue : NAME'''
        p[0] = Name(LU.i(p, 1))

    # option_directive = OPTION_ - ident("optionName") + EQ + quotedString("optionValue") + SEMI
    def p_option_directive(self, p):
        '''option_directive : OPTION NAME EQ option_rvalue SEMI'''
        p[0] = OptionStatement(Name(LU.i(p, 2)), LU.i(p, 4))
        self.lh.set_parse_object(p[0], p)

    # topLevelStatement = Group(message_definition | message_extension | enum_definition | service_definition |
    #                           import_directive | option_directive | package_definition)
    def p_topLevel(self, p):
        '''topLevel : message_definition
                    | message_extension
                    | enum_definition
                    | policy_definition
                    | map_definition
                    | reduce_definition
                    | service_definition
                    | import_directive
                    | package_directive
                    | option_directive'''
        p[0] = p[1]

    def p_statements2(self, p):
        '''statements : topLevel
                      | statements topLevel'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statements(self, p):
        '''statements : empty'''
        p[0] = []

    # parser = Optional(package_directive) + ZeroOrMore(topLevelStatement)
    def p_protofile(self, p):
        '''protofile : statements'''
        p[0] = ProtoFile(LU.i(p, 1))
        self.lh.set_parse_object(p[0], p)

    # Parsing starting point
    def p_goal(self, p):
        '''goal : STARTTOKEN protofile'''
        p[0] = p[2]

    def p_error(self, p):
        if p is None:
            # Omitting the closing brace on a message is one way to cause this to happen.
            # Looking up the call stack implies this might be when the parser hits EOF.
            raise ParsingError("Parsing Error, unknown token, maybe at end of file", None)
        else:
            raise ParsingError("Parsing Error", (p.lineno, p.lexpos, len(p.value)))


class ProtobufAnalyzer(object):

    def __init__(self):
        self.lexer = lex.lex(module=ProtobufLexer())
        self.parser = yacc.yacc(
            module=ProtobufParser(),
            start='goal',
            debug=0,
            outputdir='/tmp')

    def tokenize_string(self, code):
        self.lexer.input(code)
        for token in self.lexer:
            print(token)

    def tokenize_file(self, _file):
        if isinstance(_file, str):
            _file = open(_file)
        content = ''
        for line in _file:
            content += line
        return self.tokenize_string(content)

    def parse_string(self, code, debug=0, lineno=1, prefix='+'):
        self.lexer.lineno = lineno
        self.parser.offset = len(prefix)
        return self.parser.parse(prefix + code, lexer=self.lexer, debug=debug)

    def parse_file(self, _file, debug=0):
        if isinstance(_file, str):
            _file = open(_file)
        content = ''
        for line in _file:
            content += line
        return self.parse_string(content, debug=debug)
