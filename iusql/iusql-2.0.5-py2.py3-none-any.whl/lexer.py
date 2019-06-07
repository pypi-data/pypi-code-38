from pygments.lexer import inherit
from pygments.lexers.sql import MySqlLexer
from pygments.token import Keyword


class IusqlCliLexer(MySqlLexer):
    """Extends Uptycs lexer to add keywords."""

    tokens = {"root": [(r"\brepair\b", Keyword), (r"\boffset\b", Keyword), inherit]}
