# encoding: UTF-8

import re
from token import NAME, COLON, NUMBER, STRING, tok_name
from token import COMMENT, LBRACE, RBRACE, COMMA, LSQB, RSQB, LPAR, RPAR, ENDMARKER
from collections import namedtuple, OrderedDict, defaultdict

Token = namedtuple('Token', 'type literal line')


class Tokenizer:
    TOKENS = [(t, re.compile(p)) for t, p in [
        (NAME, r'[A-Za-z0-9][A-Za-z0-9_]*,[A-Za-z0-9_.,]*'),
        (NAME, r'[A-Za-z@][A-Za-z0-9_@]*'),
        (COLON, r':'),
        (NAME, r'\d+EP'),
        (NUMBER, r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'),
        (STRING, r'"[^"]*"'),
        (STRING, r"'[^']*'"),
        (COMMENT, r'#.*'),
        (LBRACE, r'\{'),
        (RBRACE, r'\}'),
        (COMMA, r','),
        (LSQB, r'\['),
        (RSQB, r'\]'),
        (LPAR, r'\('),
        (RPAR, r'\)'),
    ]]

    def __init__(self, readline):
        self.readline = readline
        self.line = None

    def tokenize(self):
        lineno = 0

        while True:
            self.line = self.readline()
            lineno += 1
            if len(self.line) == 0:
                break
            self.line = self.line.strip()
            while len(self.line) > 0:
                for ttype, pattern in self.TOKENS:
                    match = pattern.match(self.line)
                    if match is not None:
                        self.line = self.line[match.end():].lstrip()
                        yield Token(ttype, match.group(), lineno)
                        break
                else:
                    raise SyntaxError('unknown token in {!r}'.format(self.line))

        yield Token(ENDMARKER, 'EOF', lineno)


class Parser:
    """
      <prototxt> ::= <element> <prototxt> | TERMINAL
       <element> ::= <solver> | <layer> | <attribute>
        <solver> ::= "solver" <block>
         <layer> ::= "layer"  <block>
         <block> ::= "{" <attributes> "}"
    <attributes> ::= <attribute> <attributes> | TERMINAL
     <attribute> ::= NAME ":" <atom> | NAME <block>
          <atom> ::= NUMBER | STRING | NAME | <list> | <tuple>
          <list> ::= "[" <csv> "]"
         <tuple> ::= "(" <csv> ")"
       <literal> ::= NUMBER | STRING | NAME
           <csv> ::= <literal> "," <csv> | TERMINAL
    """
    def __init__(self, readline, legacy_mode=True):
        self.tokens = filter(lambda t: t.type != COMMENT, Tokenizer(readline).tokenize())
        self.legacy_mode = legacy_mode

    def consume(self, *types):
        required_tokens = []
        for token_type in types:
            token = next(self.tokens)
            if token.type == token_type:
                required_tokens.append(token)
            else:
                raise SyntaxError('line: {} required {}, got {!r}'.format(token.line, tok_name[token.type], token.literal))
        return required_tokens

    def parse(self):
        elements = []
        while True:
            token = next(self.tokens)  # type: Token
            if token.type == ENDMARKER:
                break
            elements.append(self.element(token))
        return elements

    def element(self, token):
        if token.type == NAME:
            if token.literal == 'solver':
                return self.solver()
            elif token.literal == 'layer':
                return self.layer()
            else:
                return self.attribute(token)
        else:
            raise SyntaxError('line {}: expected identifier, got {!r}.'.format(token.line, token.literal))

    def solver(self):
        return 'solver', self.block()

    def layer(self):
        return 'layer', self.block()

    def block(self, checked_leading=False):
        if not checked_leading:
            self.consume(LBRACE)
        return self.merge_repeated_keys(self.attributes())

    def attributes(self):
        attributes = []
        while True:
            token = next(self.tokens)
            if token.type == NAME:
                key, value = self.attribute(key=token)
                attributes.append((key, value))
            elif token.type == RBRACE:
                return attributes
            else:
                raise SyntaxError('line {}: excepted \'}}\' or key-value, got {!r}'.format(token.line, token.literal))

    def attribute(self, key=None):
        if not key:
            key = self.consume(NAME)
        token = next(self.tokens)
        if token.type == COLON:
            value = self.atom()
        elif token.type == LBRACE:
            value = self.block(checked_leading=True)
        else:
            raise SyntaxError('line {}: expected \'{{\' or \':\', got {!r}'.format(token.line, token.literal))
        return key.literal, value

    def atom(self):
        token = next(self.tokens)
        if token.type == LSQB:
            return self.list()
        elif token.type == LPAR:
            return self.tuple()
        elif token.type in {STRING, NAME, NUMBER}:
            return self.literal(token=token)
        else:
            raise SyntaxError('line {}: expect number, string, identifier, list or tuple, got {!r}'
                              .format(token.line, token.literal))

    def literal(self, token=None):
        if token is None:
            token = next(self.tokens)
        if token.type == STRING:
            return token.literal[1:-1]
        elif token.type == NAME:
            return token.literal
        elif token.type == NUMBER:
            if self.legacy_mode:
                return token.literal
            if re.match(r'^\d+$', token.literal):
                return int(token.literal)
            return float(token.literal)
        else:
            raise SyntaxError('line {}: expect number, string, identifier, got {!r}'.format(token.line, token.literal))

    def list(self):
        return self.csv(stop=RSQB)

    def tuple(self):
        return tuple(self.csv(stop=RPAR))

    def csv(self, stop):
        values = []
        while True:
            token = next(self.tokens)
            if token.type in {STRING, NAME, NUMBER}:
                values.append(self.literal(token=token))
            elif token.type == COMMA:
                continue
            elif token.type == stop:
                return values, stop
            else:
                raise SyntaxError('line {}: expect comma or literal, got {!r}'.format(token.line, token.literal))

    @staticmethod
    def merge_repeated_keys(attributes):
        counter = defaultdict(list)
        for key, value in attributes:
            counter[key].append(value)

        merged, meet = [], set()
        for key, value in attributes:
            if key not in meet:
                if len(counter[key]) == 1:
                    merged.append((key, value))
                else:
                    merged.append((key, counter[key]))
                meet.add(key)

        return merged


def is_flatten_dictionary(xs):
    if isinstance(xs, list):
        return len(xs) == 0 or isinstance(xs[0], tuple) and len(xs[0]) == 2
    return False


def recursively_dictionarize(xs):
    if is_flatten_dictionary(xs):
        return OrderedDict([(key, recursively_dictionarize(value)) for key, value in xs])
    return xs


def merge_repeated_fields(xs):
    if not is_flatten_dictionary(xs):
        return xs
    ys = defaultdict(list)
    for key, value in xs:
        ys[key].append(value)

    zs = []
    for key, value in ys.items():
        if len(value) == 1:
            value = value[0]
        zs.append((key, value))
    return zs


def build_layer(xs):
    layer = OrderedDict()
    for key, value in xs:
        if key == 'param' and not is_flatten_dictionary(value):
                value = [OrderedDict(pair if isinstance(pair, list) else [pair]) for pair in value]
        else:
            value = recursively_dictionarize(value)
        layer[key] = value
    return layer


def parse_prototxt(filename, legacy_mode=True):
    with open(filename) as fd:
        keyvalue = Parser(fd.readline, legacy_mode=legacy_mode).parse()

    props, solver, layers = [], None, []
    for key, value in keyvalue:
        if key == 'solver':
            solver = OrderedDict(merge_repeated_fields(value))
            props.append((key, solver))
        elif key == 'layer':
            layers.append(build_layer(value))
        else:
            props.append((key, recursively_dictionarize(value)))

    props = OrderedDict(merge_repeated_fields(props))
    if props and not solver and not layers:
        return props

    result = OrderedDict()
    if props:
        result['props'] = props
    if layers:
        result['layers'] = layers

    return result
