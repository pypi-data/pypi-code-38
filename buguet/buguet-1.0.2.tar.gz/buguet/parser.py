import re

class ParsingFailed(Exception):
    pass

class Literal:
    def __init__(self, value):
        self.value = value

class Name:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Var:
    def __init__(name, var1):
        self.name = name
        self.var1 = var1

class ApplyBrackets:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class ApplyDot:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Not:
    def __init__(self, value):
        self.value = value

class Mult:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Div:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Mod:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Plus:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Minus:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Lt:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Le:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Gt:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Ge:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Eq:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class NotEq:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class And:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Or:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Parser:
    def __init__(self, s):
        self.s = s.replace(" ", "")
        self.pos = 0

    def parse(self):
        res = self.parse_expression()
        if len(self.s) != self.pos:
            raise ParsingFailed()
        return res

    def parse_expression(self):
        return self.parse_or()

    def parse_literal(self):
        m = re.match('"(.*?)"', self.s[self.pos:])
        if m:
            self.pos += len(m.group(0))
            return Literal(m.group(1))

        m = re.match("\d+", self.s[self.pos:])
        if m:
            self.pos += len(m.group(0))
            return Literal(int(m.group(0)))

        m = re.match("true|false", self.s[self.pos:])
        if m:
            self.pos += len(m.group(0))
            if m.group(0) == "true":
                return Literal(True)
            else:
                return Literal(False)

    def parse_name(self):
        m = re.match("\D\w*", self.s[self.pos:])
        if m:
            self.pos += len(m.group(0))
            return Name(m.group(0))
        raise ParsingFailed()

    def parse_var(self):
        left = self.parse_name()
        while True:
            if len(self.s) == self.pos:
                break
            if self.s[self.pos] == "[":
                self.pos += 1
                e = self.parse_expression()
                if len(self.s) == self.pos:
                    raise ParsingFailed()
                if self.s[self.pos] != "]":
                    raise ParsingFailed()
                self.pos += 1
                left = ApplyBrackets(left, e)
            elif self.s[self.pos] == ".":
                self.pos += 1
                name = self.parse_name()
                left = ApplyDot(left, name)
            else:
                break
        return left

    def parse_term(self):
        literal = self.parse_literal()
        if literal:
            return literal
        if len(self.s) == self.pos:
            raise ParsingFailed()
        elif self.s[self.pos] == "!":
            self.pos += 1
            t = self.parse_term()
            return Not(t)
        elif self.s[self.pos] == "(":
            self.pos += 1
            e = self.parse_expression()
            if len(self.s) == self.pos:
                raise ParsingFailed()
            if self.s[self.pos] != ")":
                raise ParsingFailed()
            self.pos += 1
            return e
        else:
            return self.parse_var()

    def parse_product(self):
        left = self.parse_term()
        while True:
            if len(self.s) == self.pos:
                break
            if self.s[self.pos] == "*":
                self.pos += 1
                right = self.parse_term()
                left = Mult(left, right)
            elif self.s[self.pos] == "/":
                self.pos += 1
                right = self.parse_term()
                left = Div(left, right)
            elif self.s[self.pos] == "%":
                self.pos += 1
                right = self.parse_term()
                left = Mod(left, right)
            else:
                break
        return left

    def parse_sum(self):
        left = self.parse_product()
        while True:
            if len(self.s) == self.pos:
                break
            if self.s[self.pos] == "+":
                self.pos += 1
                right = self.parse_product()
                left = Plus(left, right)
            elif self.s[self.pos] == "-":
                self.pos += 1
                right = self.parse_product()
                left = Minus(left, right)
            else:
                break
        return left

    def parse_rel(self):
        left = self.parse_sum()
        while True:
            if len(self.s) == self.pos:
                break
            if self.s[self.pos:self.pos+2] == "<=":
                self.pos += 2
                right = self.parse_sum()
                left = Le(left, right)
            elif self.s[self.pos:self.pos+2] == ">=":
                self.pos += 2
                right = self.parse_sum()
                left = Ge(left, right)
            elif self.s[self.pos] == "<":
                self.pos += 1
                right = self.parse_sum()
                left = Lt(left, right)
            elif self.s[self.pos] == ">":
                self.pos += 1
                right = self.parse_sum()
                left = Gt(left, right)
            else:
                break
        return left

    def parse_eq(self):
        left = self.parse_rel()
        while True:
            if len(self.s) == self.pos:
                break
            if self.s[self.pos:self.pos+2] == "==":
                self.pos += 2
                right = self.parse_rel()
                left = Eq(left, right)
            elif self.s[self.pos:self.pos+2] == "!=":
                self.pos += 2
                right = self.parse_rel()
                left = NotEq(left, right)
            else:
                break
        return left

    def parse_and(self):
        left = self.parse_eq()
        while True:
            if len(self.s) == self.pos:
                break
            if self.s[self.pos:self.pos+2] == "&&":
                self.pos += 2
                right = self.parse_eq()
                left = And(left, right)
            else:
                break
        return left

    def parse_or(self):
        left = self.parse_and()
        while True:
            if len(self.s) == self.pos:
                break
            if self.s[self.pos:self.pos+2] == "||":
                self.pos += 2
                right = self.parse_and()
                left = Or(left, right)
            else:
                break
        return left
