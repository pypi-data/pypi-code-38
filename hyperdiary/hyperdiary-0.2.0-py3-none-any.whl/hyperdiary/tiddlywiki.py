import os
import io
from . import diary

def nice_date(dt):
    return dt.strftime("%d.%m.%Y")

def diary_to_tiddlers(diary_instance, tiddler_dir):
    entries = diary_instance.entries
    os.makedirs(tiddler_dir, exist_ok=True)

    for current in sorted(entries.keys()):
        with open(os.path.join(tiddler_dir, '{:04d}-{:02d}-{:02d}.tid'.format(current.year, current.month, current.day)), 'w') as f:
            tags = []
            day_text = io.StringIO()
            for line in entries[current]:
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
            compact_date = '{:04d}{:02d}{:02d}1200000000'.format(current.year, current.month, current.day)
            f.write('created: {0}\n'.format(compact_date))
            f.write('modified: {0}\n'.format(compact_date))
            f.write('tags: {}\n'.format(' '.join(set(tags))))
            f.write('title: {0}\n'.format(nice_date(current)))
            f.write('type: text/vnd.tiddlywik\n')
            f.write('\n')
            day_text.seek(0)
            f.write(day_text.read())
            f.write('\n')
