#! /usr/bin/env python3
# ------------------------------------------------
# Author:    krishna
# USAGE:
#       top.py <pseudocode file>
# ------------------------------------------------
import fileinput
import sly
import pygraphviz as pgv
import json
import os
import sys


def generate(code=None, debug=False):
    "Top function to generate flow chart"

    class FlowLexer(sly.Lexer):
        "Tokenize the pseudocode"

        tokens = {IF, ELSE, ELSEIF, WHILE, COND, STATE, PARAN_OPEN, PARAN_CLOSE}

        ignore = ' \t'
        ignore_comment = r'\#.*'

        ELSEIF = r'else if'
        IF = r'if'
        ELSE = r'else'
        WHILE = r'while'
        COND = r'\(.+?\)'
        PARAN_OPEN = r'\{'
        PARAN_CLOSE = r'\}'
        STATE = r'.+;'


        # Line number tracking
        @_(r'\n+')
        def ignore_newline(self, t):
            self.lineno += t.value.count('\n')

        # def error(self, t):
        #    print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        #    self.index += 1


    class FlowParser(sly.Parser):
        "Convert tokens into nested structures"

        # debugfile = 'parser.out'

        tokens = FlowLexer.tokens

        @_('block block')
        def block(self, p):
            if isinstance(p[1], tuple):
                # Do not create too many nested tuples
                return (p[0], *p[1])
            else:
                return (p[0], p[1])

        @_('ifBlock')
        def block(self, p):
            # Just the if
            return [p[0]]

        @_('ifBlock elseIfBlock')
        def block(self, p):
            # Else less full ladder
            return [p[0], p[1]]

        @_('ifBlock elseBlock')
        def block(self, p):
            # Full ladder without elseif
            return [p[0], p[1]]

        @_('ifBlock elseIfBlock elseBlock')
        def block(self, p):
            # Full ladder
            if isinstance(p[1], list):
                return [p[0], *p[1], p[2]]
            else:
                return [p[0], p[1], p[2]]

        @_('elseIfBlock elseIfBlock')
        def elseIfBlock(self, p):
            # Multiple Else Ifs
            # Make it a list
            p[0] = [p[0]]
            if isinstance(p[1], list):
                for x in p[1]:
                    p[0].append(x)
            else:
                p[0].append(p[1])

            return p[0]

        @_('ELSEIF cond PARAN_OPEN block PARAN_CLOSE')
        def elseIfBlock(self, p):
            # Single else if
            return {'node':'elseif', 'cond':p[1], 'body':p[3]}

        @_('IF cond PARAN_OPEN block PARAN_CLOSE')
        def ifBlock(self, p):
            # Single if
            return {'node':'if', 'cond':p[1], 'body':p[3]}

        @_('ELSE PARAN_OPEN block PARAN_CLOSE')
        def elseBlock(self, p):
            # Single else
            return {'node':'else', 'body':p[2]}

        @_('WHILE cond PARAN_OPEN block PARAN_CLOSE')
        def block(self, p):
            # While as a tuple
            return {'node':'while', 'cond':p[1], 'body':p[3]}

        @_('COND')
        def cond(self, p):
            # Return as a string, do not create more nested tuples
            return p[0][1:-1]

        @_('STATE')
        def block(self, p):
            return p[0][0:-1]


    class FlowBuilder:
        '''Builds Flow Chart from the AST'''

        attr = {
            'STATE': {
                'shape':'rectangle',
                'style':'rounded,filled',
                'fillcolor':'lightblue'
            },
            'COND': {
                'shape':'diamond',
                # 'style':'rounded',
                'color':'red'
            }
        }

        def __init__(self, elements):
            '''Initialize'''
            self.dot = pgv.AGraph(strict=True, directed=True, rankdir='TD')
            # self.dot.layout()

            lastElement = None
            for element in elements:
                lastElement = self.handle(element, lastElement)


        def connectFrom(self, node, lastElement=None, firstEdgeName=None):
            "Connect current element from all last elements"

            if not lastElement:
                return

            for x in lastElement:
                if firstEdgeName:
                    self.dot.add_edge(x, node, label=firstEdgeName)
                else:
                    self.dot.add_edge(x, node)

                firstEdgeName = None


        def handle(self, element, lastElement=None, firstEdgeName=None):
            '''Generate one node at a time'''

            if isinstance(element, str):
                self.dot.add_node(element, **self.attr['STATE'])
                self.connectFrom(element, lastElement, firstEdgeName)
                return [element]

            # Handle complex nodes
            if isinstance(element, list):
                # list is if ladder
                assert element[0]['node'] == 'if', "Expecting an IF here"

                # Handle IF
                self.dot.add_node(element[0]['cond'], **self.attr['COND'])
                self.connectFrom(element[0]['cond'], lastElement, firstEdgeName)

                # If else part is missing, retain the lastElement to return back
                # When else part is present, lastElement is no more required
                if element[-1]['node'] == 'else':
                    lastElement = []
                # Set the last condition

                lastCondition = element[0]['cond']

                # Handle IF block of ladder
                for x in self.handle(element[0]['body'], [element[0]['cond']], 'True'):
                    lastElement.append(x)

                # Get rid of the IF part
                element = element[1:]
                for i in range(len(element)):
                    if 'cond' in element[i]:
                        self.dot.add_node(element[i]['cond'], **self.attr['COND'])
                        self.connectFrom(element[i]['cond'], [lastCondition], 'False')
                        lastCondition = element[i]['cond']
                        for x in self.handle(element[i]['body'], [lastCondition], 'True'):
                            lastElement.append(x)
                    else:
                        for x in self.handle(element[i]['body'], [lastCondition], 'False'):
                            lastElement.append(x)

                return lastElement

            if isinstance(element, dict):
                # Should be a while here as other dicts are handled in if ladder
                self.dot.add_node(element['cond'], **self.attr['COND'])
                self.connectFrom(element['cond'], lastElement, firstEdgeName)

                # Handle while body
                lastElement = self.handle(element['body'], [element['cond']], 'True')

                # Connect back to condition
                self.connectFrom(element['cond'], lastElement)

                # While loop always exits with failed condition
                return [element['cond']]


            if isinstance(element, tuple):
                # Must of if/else body, handle in loop
                for e in element:
                    lastElement = self.handle(e, lastElement, firstEdgeName)
                    firstEdgeName = None

                return lastElement


        def write(self, file):
            '''Write to DOT file'''
            self.dot.write(file)


    '''The Main'''

    lexer = FlowLexer()
    parser = FlowParser()

    # When code is not given, get from stdin
    if code == None:
        code = "".join(fileinput.input())

    if debug:
        print(list(lexer.tokenize(code)))

    if debug:
        print(json.dumps(parser.parse(lexer.tokenize(code)), indent=4))

    # Build the dot file
    builder = FlowBuilder(parser.parse(lexer.tokenize(code)))

    builder.write('flowchart.dot')

    # Direct rendering isn't working, use system instead
    os.system('dot -T jpg -o flowchart.jpg flowchart.dot')


def main():
    generate()

if __name__ == '__main__':
    main()
