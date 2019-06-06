from collections import OrderedDict

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:|ERROR:', 'Command error'), (r'[Ss]yntax\s[Ee]rror', 'Command syntax error')])
