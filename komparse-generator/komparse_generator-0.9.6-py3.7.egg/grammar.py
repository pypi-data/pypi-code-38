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
from komparse import Grammar as BaseGrammar, \
    Sequence, OneOf, OneOrMore, Optional, Many, Ast

class Grammar(BaseGrammar):
    
    def __init__(self):
        BaseGrammar.__init__(self)
        self._init_tokens()
        self._init_rules()
        
    def _init_tokens(self):
        
        self.add_comment("--", "\n")
        self.add_comment("(*", "*)")
        self.add_string("'", "'", '#', 'STR')
        
        self.add_keyword('case_sensitive')
        self.add_keyword('comment')
        self.add_keyword('string')
        self.add_keyword('token')
        self.add_keyword('start')
        self.add_keyword('whitespace')

        self.add_token('ON', 'on')
        self.add_token('OFF', 'off')
        self.add_token('NESTABLE', 'nestable')
        self.add_token('ARROW', "->")
        self.add_token('LPAR', "\(")
        self.add_token('RPAR', "\)")
        self.add_token('QUESTION_MARK', "\?")
        self.add_token('PLUS', "\+")
        self.add_token('ASTERISK', "\*")
        self.add_token('PIPE', "\|")
        self.add_token('COMMA', ",")
        self.add_token('SEMICOLON', ";")
        self.add_token('AT', "@")
        self.add_token('TOKEN_ID', "[A-Z][A-Z0-9_]*")
        self.add_token('RULE_ID', "[a-z][a-z0-9_]*")
        self.add_token('ID', "[a-z][a-z0-9_]*")
        self.add_token('HASH', '#')
    
    def _init_rules(self):
        
        self.rule('komparse_grammar', OneOrMore(OneOf(
            self.configstmt(),
            self.tokenrule(),
            self.productionrule()
        )), is_root=True)
        
        self.rule('configstmt', OneOf(
            self.case_sensitive(),
            self.whitespace()))
        
        self.rule('case_sensitive', Sequence(
            self.CASE_SENSITIVE(),
            OneOf(
                self.ON(),
                self.OFF()
            ),
            self.SEMICOLON()))
        
        self.rule('whitespace', Sequence(
            self.WHITESPACE(),
            self.STR('wschars'),
            Many(Sequence(
                self.COMMA(),
                self.STR('wschars'))),
            self.SEMICOLON()))
        
        self.rule('tokenrule', OneOf(
            self.commentdef(),
            self.stringdef(),
            self.tokendef()
        ))
        
        self.rule('commentdef', Sequence(
            self.COMMENT(),
            self.STR('start'),
            self.STR('end'),
            Optional(self.NESTABLE('nestable')),
            self.SEMICOLON()
        ))
    
        self.rule('stringdef', Sequence(
            self.STRING(),
            self.STR('start'),
            self.STR('end'),
            Optional(self.STR('escape')),
            Optional(self.TOKEN_ID('token_id')),
            self.SEMICOLON()
        ))
        
        self.rule('tokendef', Sequence(
            self.TOKEN(),
            self.TOKEN_ID('token_id'),
            self.STR('regex'),
            self.SEMICOLON()
        ))
        
        self.rule('productionrule', Sequence(
            Optional(self.annotation('annot')),
            self.RULE_ID('rule_id'),
            self.ARROW(),
            self.branches('rhs'), 
            self.SEMICOLON()
        ))
        
        self.rule('annotation', Sequence(
            self.AT(),
            self.START()
        ))
        
        self.rule('branches', Sequence(
            self.branch('branch'),
            Many(Sequence(
                self.PIPE(),
                self.branch('branch')
            ))
        ))
        
        self.rule('branch', OneOrMore(
            Sequence(
                OneOf(
                    self.STR("keyword"),
                    self.tokenref(),
                    self.ruleref(),
                    self.group()
                ),
                Optional(self.cardinality('card'))
            )
        ))
        
        self.rule('tokenref', OneOf(
            Sequence(
                self.ID('id'),
                self.HASH(),
                self.TOKEN_ID()
            ),
            self.TOKEN_ID()
        ))

        self.rule('ruleref', OneOf(
            Sequence(
                self.ID('id'),
                self.HASH(),
                self.RULE_ID()
            ),
            self.RULE_ID()
        ))
        
        self.rule('group', Sequence(
            self.LPAR(),
            self.branches(),
            self.RPAR()
        ))
        
        self.rule('cardinality', OneOf(
            self.QUESTION_MARK(),
            self.PLUS(),
            self.ASTERISK()
        ))
        
        self._init_transforms()
        
    def _init_transforms(self):
        
        self.set_ast_transform('configstmt', self._trans_configstmt)
        self.set_ast_transform('case_sensitive', self._trans_case_sensitive)
        self.set_ast_transform('whitespace', self._trans_whitespace)
        self.set_ast_transform('tokenrule', self._trans_tokenrule)
        self.set_ast_transform('commentdef', self._trans_commentdef)
        self.set_ast_transform('stringdef', self._trans_stringdef)
        self.set_ast_transform('tokendef', self._trans_tokendef)
        
        self.set_ast_transform('productionrule', self._trans_productionrule)
        self.set_ast_transform('branches', self._trans_branches)
        self.set_ast_transform('branch', self._trans_branch)
        self.set_ast_transform('group', self._trans_group)
        self.set_ast_transform('tokenref', self._trans_tokenref)
        self.set_ast_transform('ruleref', self._trans_ruleref)
        
    def _trans_configstmt(self, ast):
        return ast.get_children()[0]
        
    def _trans_case_sensitive(self, ast):
        state = ast.get_children()[1].value
        return Ast('case_sensitive', state)

    def _trans_whitespace(self, ast):
        wschars = ast.find_children_by_id('wschars')
        ret = Ast('whitespace')
        for wschar in wschars:
            ret.add_child(Ast('wschar', wschar.value))
        return ret
    
    def _trans_tokenrule(self, ast):
        return ast.get_children()[0]
    
    def _trans_commentdef(self, ast):
        ret = Ast('commentdef')
        start = ast.find_children_by_id('start')[0]
        end = ast.find_children_by_id('end')[0]
        ret.add_child(Ast('start', start.value))
        ret.add_child(Ast('end', end.value))
        if ast.find_children_by_id('nestable'):
            ret.add_child(Ast('nestable'))
        return ret

    def _trans_stringdef(self, ast):
        ret = Ast('stringdef')
        start = ast.find_children_by_id('start')[0]
        end = ast.find_children_by_id('end')[0]
        escs = ast.find_children_by_id('escape')
        esc = escs and escs[0].value or None
        ids = ast.find_children_by_id('token_id')
        token_id = ids and ids[0].value or 'STRING'
        ret.add_child(Ast('id', token_id))
        ret.add_child(Ast('start', start.value))
        ret.add_child(Ast('end', end.value))
        if esc is not None:
            ret.add_child(Ast('escape', esc))
        return ret
    
    def _trans_tokendef(self, ast):
        ret = Ast('tokendef')
        token_id = ast.find_children_by_id('token_id')[0]
        regex = ast.find_children_by_id('regex')[0]
        ret.add_child(Ast('id', token_id.value))
        ret.add_child(Ast('regex', regex.value))
        return ret
    
    def _trans_productionrule(self, ast):
        ret = Ast('ruledef')
        annots = ast.find_children_by_id('annot')
        if annots:
            ret.set_attr('start', "true")
        id_ = ast.find_children_by_id('rule_id')[0]
        ret.add_child(Ast('id', id_.value))
        rhs = ast.find_children_by_id('rhs')[0]
        rhs.id = ""
        ret.add_child(rhs)
        return ret
    
    def _trans_branches(self, ast):
        ret = Ast('oneof')
        ret.add_children_by_id(ast, 'branch')
        children = ret.get_children()
        if len(children) != 1:
            return ret
        else:
            return children[0]
        
    def _trans_branch(self, ast):
        ret = Ast('sequence')
        children = ast.get_children()
        prev = None
        for child in children:
            if child.id == 'card':
                card_child = child.get_children()[0]
                cardinality = {
                    '?': 'optional',
                    '+': 'one-or-more',
                    '*': 'many'
                }[card_child.value]
                prev.set_attr('cardinality', cardinality)
            else:
                if child.id == "keyword":
                    child = Ast('keyword', child.value)
                ret.add_child(child)
                prev = child
                
        if len(ret.get_children()) != 1:
            return ret
        else:
            
            return prev
    
    def _trans_group(self, ast):
        return ast.get_children()[1]
    
    def _trans_tokenref(self, ast):
        children = ast.get_children()
        if len(children) == 1:
            return Ast('tokenref', children[0].value)
        else:
            ret = Ast('tokenref', children[2].value)
            ret.set_attr('data-id', children[0].value)
            return ret

    def _trans_ruleref(self, ast):
        children = ast.get_children()
        if len(children) == 1:
            return Ast('ruleref', children[0].value)
        else:
            ret = Ast('ruleref', children[2].value)
            ret.set_attr('data-id', children[0].value)
            return ret
    
