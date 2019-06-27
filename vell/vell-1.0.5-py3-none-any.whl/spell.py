import re
import sys

from bs4 import BeautifulSoup
from spellchecker import SpellChecker

import config


def removeHtmlTags2(page):
    soup = BeautifulSoup(page, features="html.parser")
    return ''.join(soup.findAll(text=True))


def get_ignore_words(path):
    ignore_words = []
    for line in open(path):
        li = line.strip()
        if not li.startswith("#"):
            ignore_words.append(line.rstrip())
    return ignore_words


def string2words(str, ignore_words):
    words_string = removeHtmlTags2(str)
    words = re.findall(r'\w+', words_string)
    return [w for w in words if w.lower() not in ignore_words]


def check():
    cfg = config.get_config()

    if not cfg:
        return
        
    history = dict()
    spell = SpellChecker()

    

    for file_name in cfg['files']:
        with open(file_name, 'r') as file:
            content = file.readline()
            index_line = 1

            # Reading each line is to be able to log which line has misspelled words
            while content:
                index_line += 1
                content = file.readline()
                words = string2words(content, cfg['ignore_words'])
                misspelled = spell.unknown(words)

                for word in misspelled:
                    # Update history of misspelled words
                    if word in history:
                        count = history[word]['count']
                        count += 1
                        history[word]['count'] = count
                        if count <= cfg['level_ignore']:
                            history[word]['paths'].append(
                                f'{file_name}:{index_line}')
                    else:
                        history[word] = {
                            'count': 1,
                            'paths': [f'{file_name}:{index_line}']
                        }

    is_found_misspelled = False

    # Log all misspelled words with theirs path
    for word in sorted(history.keys()):
        info = history[word]
        if info['count'] <= cfg['level_ignore']:
            for path in info['paths']:
                is_found_misspelled = True
                print(f"{path}: {word}")

    if not is_found_misspelled:
        print('Great! There are no misspelled word')


def main():
    if len(sys.argv) > 1:
        config.PATH = sys.argv[1]
    check()
