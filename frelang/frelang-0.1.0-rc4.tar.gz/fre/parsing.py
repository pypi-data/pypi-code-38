import functools

from . import lexing, specs


class ParserNode(object):
    def __init__(self, node_type, value = None, body = None, children = (), line = 0, column = 0):
        self.node_type = node_type
        self.value = value
        
        self.line = line
        self.column = column

        self.body = body
        self.children = tuple(children)

    def print_tree(self, level = 0):
        print('|  ' * level + '+-- Type: ' + self.node_type)

        if self.value is not None:
            if isinstance(self.value, ParserNode):
                print('|  ' * level + '+-+ Value: ')
                self.value.print_tree(level + 2)

            else:
                print('|  ' * level + '+-- Value: ' + repr(self.value))

        if self.body is not None:
            print('|  ' * level + '+--+ Body: ')
            self.body.print_tree(level + 1)
            print('|  ' * level + '|')

        if len(self.children) > 0:
            print('|  ' * level + '+--+ Children: ')
            
            for c in self.children:
                if c is None:
                    print('|  ' * (level + 1) + '+-- (none)')

                else:
                    c.print_tree(level + 2)

            print('|  ' * level + '|')

        if level > 0:
            print('|  ' * level)

class FreParser(object):
    def __init__(self, spec):
        self.lexer = lexing.FreLexer(spec)
        self.spec = spec

    def make_node(self, *args, **kwargs):
        return ParserNode(*args, line = self.lexer.input.line, column = self.lexer.input.column, **kwargs)

    def write(self, data):
        self.lexer.write(data)

    def skip_keyword(self, keyword):
        tok = self.next_any()

        if tok.type != 'keyword' or tok.value != keyword:
            self.error('Expected a keyword "{}"; got {} "{}"'.format(keyword, tok.type, tok.value))

    def is_keyword(self, keyword):
        if self.end():
            return False

        tok = self.lexer.peek()

        return tok.type == 'keyword' and tok.value == keyword

    def is_punctuation(self, char):
        if self.end():
            return False

        tok = self.lexer.peek()

        return tok.type == 'punctuation' and tok.value == char

    def expect_punctuation(self, *chars):
        if self.end():
            self.error("Expected punctuation (either of {}); got end of file instead.".format(', '.join(repr(x) for x in chars)))

        tok = self.lexer.peek()

        if not (tok.type == 'punctuation' and tok.value in chars):
            self.error("Expected punctuation (either of {}); got {} \"{}\"".format(', '.join(repr(x) for x in chars), tok.type, tok.value))

    def skip_punctuation(self, char):
        if self.end():
            self.error("Expected punctuation '{}'; got end of file instead.".format(char))

        tok = self.lexer.peek()

        if not (tok.type == 'punctuation' and tok.value == char):
            self.error("Expected punctuation '{}'; got {} \"{}\"".format(char, tok.type, tok.value))

        self.next_any()

    def skip_any(self):
        next(self.lexer)

    def next_any(self):
        return next(self.lexer)

    def error(self, msg):
        self.lexer.error(msg)

    def next_type(self):
        if self.end():
            self.error("Expected a type; got end of file instead.")

        acc = ''

        while True:
            tok = self.lexer.peek()

            if tok.type == 'type' or (tok.type == 'punctuation' and tok.value in '()'):
                acc += tok.value
                self.skip_any()
                
            elif not acc:
                self.error("Expected a type; got {} \"{}\"".format(tok.type, tok.value))

            else:
                break

        return self.make_node('type', acc)

    def next_operator(self):
        if self.end():
            self.error("Expected an operator; got end of file instead.")
        
        tok = self.next_any()

        if tok.type != 'operator':
            self.error("Expected an operator; got {} \"{}\"".format(tok.type, tok.value))
        
        return tok.value

    def next_identifier(self, can_mod = False):
        if self.end():
            self.error("Expected an identifier; got end of file instead.")

        tok = self.next_any()

        if tok.type != 'identifier':
            self.error("Expected an identifier; got {} \"{}\"".format(tok.type, tok.value))

        # Extract modifier
        mods = ''
        acc = ''
        
        for t in tok.value:
            if t in self.spec.identifier_modifiers and not acc:
                if not can_mod:
                    self.error("Identifier modifier not expected here!")

                mods += t

            else:
                acc += t

        if can_mod:
            return (acc, mods)

        else:
            return acc

    def is_type(self, *ttypes):
        if self.end():
            return False

        tok = self.lexer.peek()

        return tok.type in ttypes

    def end(self):
        return self.lexer.peek() is None

    def parse_arg_defs(self):
        self.skip_punctuation('(')

        defs = []

        while True:
            if self.is_punctuation(')'):
                self.skip_punctuation(')')
                break

            atype = self.next_type()
            aname = self.next_identifier()

            defs.append(self.make_node('expr.argdef', aname, body = atype))
            self.expect_punctuation(',', ')')

            if self.is_punctuation(','):
                self.skip_punctuation(',')

            else:
                self.skip_punctuation(')')
                break

        return defs

    def parse_func(self):
        self.skip_keyword('func')

        return_type = self.next_type()

        if self.is_type('identifier'):
            fname = self.next_identifier()

        else:
            fname = None

        children = self.subparser('func.arglist', self.parse_arg_defs)
        body = self.subparser('statement', self.parse_statement)

        node = self.make_node('expr.func', fname, return_type, (body, *children))

        return node

    def parse_args(self):
        self.skip_punctuation('(')
        res = []

        while True:
            if self.is_punctuation(')'):
                self.skip_punctuation(')')
                break

            r = self.subparser('arglist.expr', self.parse_expr)
            res.append(r)

            self.expect_punctuation(',', ')')

            if self.is_punctuation(','):
                self.skip_punctuation(',')

            else:
                self.skip_punctuation(')')
                break

        return res

    def parse_func_call(self, name):
        return self.make_node('expr.funcall', name, children = self.subparser('expr.funcall.arglist', self.parse_args))

    def parse_expr(self):
        if self.is_punctuation('('):
            self.skip_punctuation('(')
            expr = self.subparser('expr.subexpr', self.parse_expr)
            self.skip_punctuation(')')

            return expr

        tok = self.lexer.peek()

        if tok.type == 'identifier':
            name, mods = self.next_identifier(True)

            if self.is_punctuation('('):
                if mods != '':
                    self.error("Identifier modifiers not supported in function calls!")

                return self.subparser('expr.funcall', self.parse_func_call, name)

            else:
                return self.make_node('expr.identifier', (name, mods))

        elif tok.type == 'number':
            self.next_any()
            return self.make_node('expr.literal.int', tok.value)

        elif tok.type == 'number.float':
            self.next_any()
            return self.make_node('expr.literal.float', tok.value)

        elif tok.type == 'string':
            self.next_any()
            return self.make_node('expr.literal.string', tok.value)

        elif tok.type == 'value':
            self.next_any()
            return self.make_node('expr.literal.value', tok.value)

        elif tok.type == 'operator':
            return self.subparser('expr.oper', self.parse_operation)

        elif tok.type == 'keyword' and tok.value == 'func':
            return self.subparser('expr.func', self.parse_func)

        elif tok.type == 'keyword' and tok.value == 'set':
            return self.subparser('expr.set', self.parse_set)

        else:
            self.error("Expected expression; got {} \"{}\"".format(tok.type, tok.value))

    def parse_operands(self):
        res = []

        while True:
            res.append(self.subparser('expr.oper.operands.expr', self.parse_expr))
            do_next = self.is_punctuation(',')

            if do_next:
                self.skip_punctuation(',')

            else:
                break

        return res

    def parse_define_var(self):
        kind = self.next_type()
        name, mods = self.next_identifier(True)
        value = None

        if self.is_punctuation(','):
            self.skip_punctuation(',')

            if mods == '':
                value = self.subparser('var.value_expr', self.parse_expr)

            else:
                value = self.next_identifier(True)

        return self.make_node('vardef', (name, mods, value), body = kind)

    def parse_operation(self):
        operator = self.next_operator()
        operands = self.subparser('expr.oper.operands', self.parse_operands)

        return self.make_node('expr.oper', operator, children = operands)

    def parse_set(self):
        self.skip_keyword('set')
        
        var = self.next_identifier(True)
        self.skip_punctuation(',')
        val = self.subparser('set.value', self.parse_expr)

        return self.make_node('expr.set', var, body = val)

    def parse_condition(self):
        self.skip_punctuation('(')
        expr = self.subparser('condition.expr', self.parse_expr)
        self.skip_punctuation(')')

        return expr

    def parse_if(self):
        self.skip_keyword('if')
        condition = self.subparser('if.condition', self.parse_condition)
        body = self.subparser('if.body', self.parse_statement)

        if self.is_keyword('else'):
            self.skip_keyword('else')
            else_body = self.subparser('if.else', self.parse_statement)

        else:
            else_body = None

        return self.make_node('logic.if', children = (condition, self.make_node('logic.else', body = else_body)), body = body)

    def parse_while(self):
        self.skip_keyword('while')
        condition = self.subparser('while.condition', self.parse_condition)
        body = self.subparser('while.body', self.parse_statement)

        if self.is_keyword('else'):
            self.skip_keyword('else')
            else_body = self.subparser('while.else', self.parse_statement)

        else:
            else_body = None

        return self.make_node('logic.while', children = (condition, self.make_node('logic.else', body = else_body)), body = body)

    def parse_return(self):
        self.skip_keyword('return')
        value = self.subparser('return.value', self.parse_expr)
        return self.make_node('return', body = value)

    def parse_regular_statement(self):
        tok = self.lexer.peek()

        if tok.type == 'keyword':
            if tok.value == 'return':
                return self.subparser('return', self.parse_return)

            elif tok.value == 'set':
                return self.subparser('expr.set', self.parse_set)

            elif tok.value == 'break':
                self.skip_any()
                return ParserNode('break')

            elif tok.value == 'continue':
                self.skip_any()
                return ParserNode('continue')

            else:
                self.error("Expected statement; got {} \"{}\"".format(tok.type, tok.value))

        elif tok.type == 'operator':
            return self.subparser('expr.oper', self.parse_operation)

        elif tok.type == 'type':
            return self.subparser('type', self.parse_define_var)

        elif tok.type == 'identifier':
            return self.subparser('expr', self.parse_expr)

        else:
            self.error("Expected statement; got {} \"{}\"".format(tok.type, tok.value))

    def parse_statement(self):
        if self.end():
            return None

        elif self.is_punctuation(';'):
            self.skip_punctuation(';')
            return self.make_node('pass')

        elif self.is_punctuation('{'):
            children = []

            self.skip_punctuation('{')

            while True:
                if self.end():
                    self.error('Expected "}" before end of file!')

                elif self.is_punctuation('}'):
                    self.skip_punctuation('}')
                    break

                else:
                    children.append(self.subparser('statement', self.parse_statement))

            return self.make_node('block', children = children)

        else:
            tok = self.lexer.peek()

            if tok.type == 'keyword':
                if tok.value == 'func':
                    return self.subparser('expr.func', self.parse_func)

                elif tok.value == 'if':
                    return self.subparser('logic.if', self.parse_if)
                    
                elif tok.value == 'while':
                    return self.subparser('logic.while', self.parse_while)

            res = self.parse_regular_statement()
            self.skip_punctuation(';')
            return res

    def subparser(self, name, func, *args, **kwargs):
        return self.lexer.input.call(name, func, *args, **kwargs)

    @classmethod
    def parse(cls, data, spec = None):
        spec = spec or specs.FreSpecs()

        parser = cls(spec)
        parser.write(data)
        
        return (parser, iter(functools.partial(parser.subparser, 'parser', parser.parse_statement), None))

def main():
    import sys

    data = sys.stdin.read()

    for x in FreParser.parse(data, spec = specs.FreSpecs)[1]:
        x.print_tree()

    return

if __name__ == "__main__":
    main()