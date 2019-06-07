from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser(
        description='Reports unused imports in a ES6 javascript file')

    # Add arguments to the parser here
    parser.add_argument('name', nargs='+')
    return Dodo.parse_args(parser)


ignore_list = [
    '*', '{', '}', 'import', 'as', 'type', 'React', '__RewireAPI__',
    '$FlowFixMe'
]
stop_words = [';', 'from']


def _is_quoted(x):
    for quote in ('"', "'"):
        if x.startswith(quote) and x.endswith(quote):
            return True
    return False


def _process(filename):
    with open(filename) as ifs:
        lines = ifs.readlines()

    keywords, body, scanning = [], "", False

    for idx in range(len(lines)):
        if lines[idx].startswith('import'):
            scanning = True

        if scanning:
            line = lines[idx].replace(',', '')
            for stop_word in stop_words:
                pos = line.find(stop_word)
                if pos >= 0:
                    line = line[:pos]
                    scanning = False
            keywords += [
                x for x in line.split()
                if x not in ignore_list and not _is_quoted(x)
            ]
        else:
            body += lines[idx]

    unused = [x for x in keywords if x not in body]
    if unused:
        print('\n[%s]' % filename)
        for keyword in unused:
            print(keyword)


if Dodo.is_main(__name__, safe=True):
    args = _args()
    for filename in args.name:
        _process(filename)
