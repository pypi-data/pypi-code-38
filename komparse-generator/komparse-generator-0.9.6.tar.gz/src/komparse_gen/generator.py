"""
Copyright 2018 Thomas Bollmeier <entwickler@tbollmeier.de>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""   
import sys
import os
from argparse import ArgumentParser
from komparse import Parser
from .grammar import Grammar
from .output import StdOut, FileOut


class Generator(object):
    
    def __init__(self, tabsize=4):
        self._parser = Parser(Grammar())
        self._tabsize = tabsize
    
    def generate(self, grammar_source, parser_name, output=StdOut()):
        
        ast = self._parser.parse(grammar_source)
        if not ast:
            raise Exception(self._parser.error())
        
        self._output = output
        self._indent_level = 0
        self._num_seqs = 0
        self._sequences = {}
        self._num_oneofs = 0
        self._oneofs = {}
        
        case_sensitive = self._is_case_sensitive(ast)
        wspace = self._get_whitespace(ast) 
        tokens, rules = self._get_tokens_and_rules(ast)
        self._find_keywords(ast)
        
        self._output.open()
        
        try:        
            self._wrt_imports()
            self._writeln()
            self._writeln()
            self._writeln("class _Grammar(Grammar):")
            self._indent()
            self._writeln()
            self._writeln("def __init__(self):")
            self._indent()
            self._writeln("Grammar.__init__(self, case_sensitive={}, wspace={})".format(case_sensitive, wspace))
            self._writeln("self._init_tokens()")
            self._writeln("self._init_rules()")
            self._dedent()
            self._writeln()
            self._wrt_init_tokens(tokens)
            self._writeln()
            self._wrt_init_rules(rules)
            self._writeln()
            self._wrt_sequences()
            self._wrt_oneofs()
            self._writeln()
            self._dedent()
            self._writeln("class {}(Parser):".format(parser_name))
            self._indent()
            self._writeln()
            self._writeln("def __init__(self):")
            self._indent()
            self._writeln("Parser.__init__(self, _Grammar())")
            self._writeln()
            self._dedent()
            self._writeln()
        except Exception as exc:
            self._output.close()
            raise exc
            
        self._output.close()
        
    def _is_case_sensitive(self, ast):
        case_sensitive = True
        for child in ast.get_children():
            if child.name == "case_sensitive":
                case_sensitive = child.value == "on"
                break
        return case_sensitive
    
    def _get_whitespace(self, ast):
        ws = ast.find_children_by_name('whitespace')
        if ws:
            ws = ws[0]
            ret = "["
            first = True
            for wschar in ws.get_children():
                if not first:
                    ret += ", "
                else:
                    first = False
                ret += '"{}"'.format(wschar.value)
            ret += "]"
            return ret
        else:
            return '[" ", "\\t", "\\r", "\\n"]'
        
    def _get_tokens_and_rules(self, ast):
        tokens = []
        rules = []
        for child in ast.get_children():
            if child.name == "ruledef":
                rules.append(child)
            else:
                tokens.append(child)
        return tokens, rules
    
    def _find_keywords(self, ast):
        self._keywords = {}
        ast.walk(self)
        
    def enter_node(self, node):
        pass
    
    def exit_node(self, node):
        pass
        
    def visit_node(self, node):
        if node.name == "keyword":
            kw = node.value
            self._keywords[kw.upper()] = kw
        
    def _wrt_init_tokens(self, tokens):
        self._writeln("def _init_tokens(self):")
        self._indent()
        for token in tokens:
            if token.name == "commentdef":
                self._wrt_commentdef(token)
            elif token.name == "stringdef":
                self._wrt_stringdef(token)
            elif token.name == "tokendef":
                self._wrt_tokendef(token)
        for kw in self._keywords.values():
            self._writeln("self.add_keyword('{}')".format(kw))
        self._dedent()
        
    def _wrt_commentdef(self, commentdef):
        children = commentdef.get_children()
        if len(children) == 2:
            start, end = children
            line = "self.add_comment('{}', '{}')".format(start.value, end.value)
        else:
            start, end, _ = children
            line = "self.add_comment('{}', '{}', nestable=True)".format(start.value, end.value)
        self._writeln(line)
        
    def _wrt_stringdef(self, stringdef):
        children = stringdef.get_children()
        if len(children) == 3:
            id_, start, end = map(lambda it: it.value, children)
            line = "self.add_string('{}', '{}', name='{}')".format(start, end, id_)
        else:
            id_, start, end, esc = map(lambda it: it.value, children)
            line = "self.add_string('{}', '{}', '{}', '{}')".format(start, end, esc, id_)
        self._writeln(line)
        
    def _wrt_tokendef(self, tokendef):
        id_, regex = tokendef.get_children()
        line = "self.add_token('{}', '{}')".format(id_.value, regex.value)
        self._writeln(line)
        
    def _wrt_init_rules(self, rules):
        self._writeln("def _init_rules(self):")
        self._indent()
        for rule in rules:
            self._wrt_rule(rule)
        self._dedent()
        
    def _wrt_rule(self, rule):
        id_, content = rule.get_children()
        call = self._get_call(content)
        is_start = rule.has_attr('start') and rule.get_attr('start') == "true"
        if not is_start:
            line = "self.rule('{}', {})".format(id_.value, call)
        else:
            line = "self.rule('{}', {}, is_root=True)".format(id_.value, call)
        self._writeln(line)
        
    def _wrt_internal_funcs(self, fn_dict):
        names = list(fn_dict.keys())
        names.sort()
        for name in names:
            self._writeln("def {}(self):".format(name))
            self._indent()
            for line in fn_dict[name]:
                self._writeln(line)
            self._dedent()
            self._writeln()
            
    def _wrt_sequences(self):
        self._wrt_internal_funcs(self._sequences)
        
    def _wrt_oneofs(self):
        self._wrt_internal_funcs(self._oneofs)

    def _get_call(self, content):
        name = content.name
        id_ = ""
        if name == "oneof":
            self._num_oneofs += 1
            func_name = "_oneof_{}".format(self._num_oneofs)
            self._oneofs[func_name] = self._get_func_body(content)
        elif name == "sequence":
            self._num_seqs += 1
            func_name = "_seq_{}".format(self._num_seqs)
            self._sequences[func_name] = self._get_func_body(content)
        elif name in ["ruleref", "tokenref"]:
            func_name = content.value
            if content.has_attr('data-id'):
                id_ = content.get_attr('data-id')
        elif name == "keyword":
            func_name = content.value.upper()
        else:
            raise RuntimeError("Unknown content")
        
        if not id_:
            call = "self." + func_name + "()"
        else:
            call = "self." + func_name + "('" + id_ + "')"
            
        if content.has_attr('cardinality'):
            card = content.get_attr('cardinality')
            call = {
                "optional": "Optional(" + call + ")",
                "one-or-more": "OneOrMore(" + call + ")",
                "many": "Many(" + call + ")"
            }[card]
                
        return call
    
    def _get_func_body(self, content):
        lines = []
        if content.name == "oneof":
            lines.append("return OneOf(")
        elif content.name == "sequence":
            lines.append("return Sequence(")
        else:
            raise RuntimeError("Unknown content")
        children = content.get_children()
        max_idx = len(children) - 1 
        left_pad = " " * self._tabsize
        for idx, child in enumerate(children):
            line = left_pad + self._get_call(child)
            if idx < max_idx:
                line += ","
            else:
                line += ")"
            lines.append(line)
        return lines
            
    def _wrt_imports(self):
        self._writeln("from komparse import Parser, Grammar, Sequence, OneOf, \\")
        self._indent()
        self._writeln("Optional, OneOrMore, Many")
        self._dedent()
        
    def _writeln(self, line=""):
        self._output.writeln(" " * self._indent_level * self._tabsize + line)
        
    def _indent(self):
        self._indent_level += 1
        
    def _dedent(self):
        self._indent_level -= 1


def _read_file_content(filepath):
    content = ""
    fp = open(filepath, "r")
    lines = fp.readlines()
    fp.close()
    for line in lines:
        content += line
    return content


def generate():
    
    parser = ArgumentParser('Generate a parser')
    parser.add_argument('grammar_file')
    parser.add_argument('-o', '--outfile',
                        help='filepath to store the generated parser',
                        dest='outfile')
    parser.add_argument('-n', '--name',
                        help='name of the parser',
                        dest='parser_name')
    
    args = parser.parse_args()
    
    grammar_file = args.grammar_file
    
    if args.parser_name:
        parser_name = args.parser_name
    else:
        parser_name = os.path.basename(grammar_file).split(".")[0]
        parser_name = parser_name.capitalize() + "Parser"
        
    if args.outfile:
        output = FileOut(args.outfile)
    else:
        output = StdOut()
        
    code = _read_file_content(grammar_file)
    
    Generator().generate(code, parser_name, output)
