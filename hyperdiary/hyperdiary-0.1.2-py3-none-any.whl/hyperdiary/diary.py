import re, enum
from datetime import datetime
from collections import namedtuple
import yaml
import json
from pathlib import Path

def get_files():
    path = Path('.').resolve()
    while not (path / 'hyperdiary.json').exists() and len(path.parts) > 1:
        path = path.parent
    project_json = path / 'hyperdiary.json'
    if not project_json.exists():
        raise Exception('No hyperdiary.json found in any parent directories')
    with open(str(project_json), 'r') as f:
        return [str(path / f) for f in json.load(f)['sources']]

def load_all():
    entries = dict()

    for fname in get_files():
        with open(fname) as f:
            for dt, entry in yaml.load(f, Loader=yaml.SafeLoader).items():
                if dt in entries:
                    raise Exception('Double definition for {0} in file {1}'.format(dt, fname))
                entries[dt] = entry

    return entries

@enum.unique
class EntryType(enum.Enum):
    Line = 1
    Dict = 2
    DictLine = 3

def iter_entries(yml):
    for date, entries in yml.items():
        #date = datetime.strptime(date, '%Y-%m-%d').date() not required, apperently already parsed to date object
        for entry in entries:
            if isinstance(entry, str):
                yield (date, entry, EntryType.Line)
            elif isinstance(entry, dict):
                for k, v in entry.items():
                    yield (date, k, EntryType.Dict)
                    for l in v:
                        yield (date, l, EntryType.DictLine)

def find_tags(line):
    '''
    >>> res = [t.text for t in find_tags("+tag1 +tag2 some content goes here +tag3")]
    >>> res == ["tag1", "tag2", "tag3"]
    True
    '''
    return find(line, TokenType.Tag)

def find_ids(line):
    return find(line, TokenType.Id)

def find(line, token_type):
    return [token for token in tokenize(line) if token.type == token_type]

@enum.unique
class TokenType(enum.Enum):
    Text = 1
    Tag = 2
    Id = 3


_REPLACEMENTS = {
    '&': 'and',
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'ß': 'ss',
    '\'': ''
}
def make_id(sid):
    sid = sid.lower()
    for k, v in _REPLACEMENTS.items():
        sid = sid.replace(k, v)
    assert not ' ' in sid, sid
    return sid

def _capitalize(s):
    up = True
    for l in s:
        if up:
            yield l.upper()
            up = False
        else:
            if l == ' ':
                up = True
            yield l
def beautify_id(sid):
    return ''.join(_capitalize(sid.replace('_', ' ')))

class Token:
    def __init__(self, type, text, ref=None):
        self.type = type
        self.text = text
        self.ref = ref
        if type == TokenType.Id:
            if not ref:
                s = text.split('|', 1)
                self.text = beautify_id( s[1] if len(s)==2 else s[0] )
                self.ref = make_id(s[0])

    def __repr__(self):
        return 'Token({0}, "{1}", "{2}")'.format(self.type, self.text, self.ref)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        if self.type == TokenType.Id and other.type == TokenType.Id:
            return self.ref == other.ref
        return self.type == other.type and self.text == other.text and self.ref == other.ref

    def __hash__(self):
        if self.type == TokenType.Id:
            return hash(self.type) ^ hash(self.ref)
        return hash(self.type) ^ hash(self.text) ^ hash(self.ref)

    def __lt__(self, other):
        return self.text < other.text

re_separator = re.compile(' |;|,|\\.')
def _fragmented_tokenize(line):
    current = []
    current_type = TokenType.Text
    for l in line:
        if re_separator.match(l):
            if current:
                yield Token(current_type, ''.join(current))
            yield Token(TokenType.Text, l)
            current = []
            current_type = TokenType.Text
            continue
        if not current:
            if l == '+':
                current_type = TokenType.Tag
            elif l == '$':
                current_type = TokenType.Id
            else:
                current_type = TokenType.Text
            current.append(l if current_type == TokenType.Text else '')
            continue
        current.append(l)
    if current:
        yield Token(current_type, ''.join(current))


def tokenize(line):
    text_token = Token(TokenType.Text, '')
    for next in _fragmented_tokenize(line):
        if next.type == TokenType.Text:
            text_token = Token(TokenType.Text, text_token.text + next.text)
        else:
            if text_token.text:
                yield text_token
                text_token = Token(TokenType.Text, '')
            yield next
    if text_token.text:
        yield text_token

if __name__ == '__main__':
    line = '+tag A $test-line by $Jane_Doe|Jane; expect no content +hallo'
    print(find_tags(line))
    print(find_ids(line))
    print(list(tokenize(line)))
