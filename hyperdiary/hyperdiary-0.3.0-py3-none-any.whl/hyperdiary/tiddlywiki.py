import os
import io
from . import diary

class Tiddler:
    def __init__(self, **fields):
        self.fields = dict(**fields)
    
    @property
    def title(self):
        return self.fields['title']
    
    @property
    def text(self):
        return self.fields['text']
    
    def __str__(self):
        return '<Tiddler(title="{0}")>'.format(self.title)
    
    def __repr__(self):
        return 'Tiddler({0})'.format(', '.join(
            '{}="{}"'.format(k, v) for k, v in self.fields.items()))
    
    def _fields_without_text(self):
        for key, val in self.fields.items():
            if key.lower() != 'text':
                yield key, val
    
    def to_tid(self):
        return '\n'.join(['{} = {}'.format(k, v) for k, v in self._fields_without_text()]) \
            + '\ntype: text/vnd.tiddlywik\n\n' \
            + self.text
    
    def to_div(self):
        args = ' '.join(['{}="{}"'.format(k, v) for k, v in self._fields_without_text()])
        return '<div {}>\n<pre>\n{}\n</pre>\n</div>'.format(args, self.text)
    
    @staticmethod
    def from_entry(dt, entry):
        tags = []
        day_text = io.StringIO()
        for line in entry:
            day_text.write('* ')
            for token in diary.tokenize(line):
                if token.type == diary.TokenType.Id:
                    day_text.write('[[{}|{}]]'.format(token.text, token.ref))
                elif token.type == diary.TokenType.Text:
                    day_text.write(token.text)
                elif token.type == diary.TokenType.Tag:
                    tags.append(token.text)
                else:
                    raise NotImplementedError('Unknown TokenType')
            day_text.write('\n')
        day_text.seek(0)
        compact_date = '{:04d}{:02d}{:02d}1200000000'.format(dt.year, dt.month, dt.day)

        fields = dict(title=nice_date(dt),
                      text=day_text.read(),
                      tags=' '.join(sorted(set(tags))),
                      created=compact_date,
                      modified=compact_date)
        
        return Tiddler(**fields)



def nice_date(dt):
    return dt.strftime("%d.%m.%Y")


def diary_to_tiddlers(diary_instance):
    entries = diary_instance.entries
    for dt in sorted(entries.keys()):
        yield dt, Tiddler.from_entry(dt, entries[dt])


def diary_to_tiddlers_export(diary_instance, tiddler_dir):
    os.makedirs(tiddler_dir, exist_ok=True)
    for dt, tiddler in diary_to_tiddlers(diary_instance):
        fname = '{:04d}-{:02d}-{:02d}.tid'.format(dt.year, dt.month, dt.day)
        with open(os.path.join(tiddler_dir, fname), 'w') as f:
            f.write(tiddler.to_tid())

_STORE_AREA_SENTINEL = 'id="storeArea"'

def diary_to_tiddlywiki_export(diary_instance, file, tiddlywiki_base_file):
    content = '\n'.join(tiddler.to_div() for dt, tiddler in diary_to_tiddlers(diary_instance))
    sentinel_found = False
    with open(file, 'w') as f, open(tiddlywiki_base_file, 'r') as wiki:
        for line in wiki:
            f.write(line)
            if _STORE_AREA_SENTINEL in line:
                f.write(content)
                sentinel_found = True
    if not sentinel_found:
        raise Exception('Could not find \'{}\' in file {}' \
                        .format(_STORE_AREA_SENTINEL, tiddlywiki_base_file))
            
