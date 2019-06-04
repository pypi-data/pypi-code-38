"""
    Copyright 2017 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""

from pygments.lexer import RegexLexer, bygroups
from pygments.token import Name, Whitespace, Operator, Comment, Token, Keyword, Number, String

from inmanta.parser.plyInmantaLex import keyworldlist


primitives = ["bool", "string", "number", "list", "dict"]

in_class_name = r'((?:[a-zA-Z_0-9-]+::)*[A-Z][a-zA-Z_0-9-]*)'
whitespace = r'([\t ]+)'
ident = r'([a-zA-Z_0-9-]+)'
multi = r'(?:[:](?:[0:9]+)?)?](?:[\t ]+)--(?:[\t ]+)\[[0-9]*(?:[:](?:[0:9]+)?)?])'
multi_like = r'(\[[0-9: \t]+\][\t -]*\[[0-9: \t]+\])'
multihalf_like = r'(\[[0-9: \t]+\][\t -]*)'

dot = r'([.])'

oldstyle = in_class_name + whitespace + ident + whitespace + multi_like + whitespace + in_class_name + whitespace + ident


class InmantaLexer(RegexLexer):

    name = 'Inmanta'
    aliases = ['inmanta']
    filenames = ['*.cf']

    def process_id(self, match):
        text = match.group(0)
        if(text in keyworldlist):
            tokentype = Keyword
        elif text in primitives:
            tokentype = Name.Builtin
        else:
            tokentype = Name
        yield match.start(), tokentype, text

    tokens = {
        'root': [
            (r'(entity)([ \t]+)([a-zA-Z_][a-zA-Z_0-9-]*)', bygroups(Keyword, Whitespace, Name.Class), 'entity-extend'),
            # old style relation Host mgr [0:] -- [1] odl::ODL odl
            (in_class_name + whitespace + ident + whitespace + multi_like + whitespace + in_class_name + whitespace + ident,
             bygroups(Name.Class, Whitespace, Name.Function, Whitespace,
                      Operator, Whitespace, Name.Class, Whitespace, Name.Function)),
            # new style relation File.host [1] -- Host.files [0:]
            (in_class_name + dot + ident + whitespace + multi_like + whitespace + in_class_name + dot + ident,
             bygroups(Name.Class, Operator, Name.Function, Whitespace,
                      Operator, Whitespace, Name.Class, Operator, Name.Function)),
            # new style relation File.host [1] -- Host
            (in_class_name + dot + ident + whitespace + multihalf_like + whitespace + in_class_name,
             bygroups(Name.Class, Operator, Name.Function, Whitespace,
                      Operator, Whitespace, Name.Class)),
            (in_class_name, Name.Class),
            ("[\"]{3}([\\n]|.)*?[\"]{3}", Comment.Multiline),  # t_begin_mls
            ("\n+", Whitespace),  # t_ANY_newline
            ('!=|==|>=|<=|<|>', Token.Operator),  # t_CMP_OP
            ('[:[\]()=,.{}]', Token.Operator),  # literals
            ("\#.*?\n", Comment.Single),  # t_COMMENT
            ("[-]?[0-9]*[.][0-9]+", Number.Float),  # t_FLOAT
            ("[a-zA-Z_][a-zA-Z_0-9-]*", process_id),  # t_ID
            ("[-]?[0-9]+", Number.Integer),  # t_INT
            ("\//.*?\n", Comment.Single),  # t_JCOMMENT
            ("/[^/]*/", String.Regex),  # t_REGEX
            ("--|->|<-", Token.Operator),  # t_REL
            ("[:]{2}", Name),  # t_SEP
            (r'\".*?[^\\]\"', String),  # t_STRING
            ("\"\"", String),  # t_STRING_EMPTY
            ("[ \t]+", Whitespace)  # t_ignore

        ],

        'entity-extend': [
            ("[ \t]+", Whitespace),  # t_ignore
            ('extends', Keyword),
            (in_class_name, Name.Class),
            (r',', Token.Operator),
            (r':', Token.Operator, "#pop")
        ]
    }
