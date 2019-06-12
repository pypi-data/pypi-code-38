from argparse import ArgumentParser
from datetime import datetime, date, timedelta

import yaml

from .diary import Diary
from .check import check
from .stats import stats
from .html import diary_to_html, diary_to_html_folder
from .hugo import diary_to_hugo
from .tiddlywiki import diary_to_tiddlers
from .view import view

diary_path = '.'

parser = ArgumentParser(description='The hyperdiary main command line interface.')
subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', help='Available subcommands')
subparsers.required = True

check_parser = subparsers.add_parser('check', help='Check entire diary for integrity up-to-dateness')
def _check_exec(args):
    print('Checking diary...')
    check(Diary.discover_and_load(diary_path))
check_parser.set_defaults(func=_check_exec)

stats_parser = subparsers.add_parser('stats', help='Calculate impressive diary statistics')
stats_parser.add_argument('file', nargs='?')
def _stats_exec(args):
    print('Stats\n-----')
    if args.file:
        with open(args.file) as f:
            entries = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        entries = Diary.discover_and_load(diary_path).entries
    stats(entries)
stats_parser.set_defaults(func=_stats_exec)

html_parser = subparsers.add_parser('html', help='Export diary to html')
html_parser.add_argument('file')
def _html_exec(args):
    print('Exporting diary in HTML to {}'.format(args.file))
    diary_to_html(Diary.discover_and_load(diary_path), args.file)
html_parser.set_defaults(func=_html_exec)

html_folder_parser = subparsers.add_parser('htmlfolder', help='Export diary to html in folders')
html_folder_parser.add_argument('folder')
def _html_folder_exec(args):
    print('Exporting diary in HTML to {}'.format(args.folder))
    diary_to_html_folder(Diary.discover_and_load(diary_path), args.folder)
html_folder_parser.set_defaults(func=_html_folder_exec)

hugo_parser = subparsers.add_parser('hugo', help='Export diary to hugo static site format')
hugo_parser.add_argument('folder')
def _hugo_exec(args):
    print('Exporting diary in hugo static site format to {}'.format(args.folder))
    diary_to_hugo(Diary.discover_and_load(diary_path), args.folder)
hugo_parser.set_defaults(func=_hugo_exec)

tiddler_parser = subparsers.add_parser('tiddlers', help='Export diary to tiddlywiki tiddlers format')
tiddler_parser.add_argument('folder')
def _tiddlywiki_exec(args):
    print('Exporting diary in tiddlywiki tiddlers format to {}'.format(args.folder))
    diary_to_tiddlers(Diary.discover_and_load(diary_path), args.folder)
tiddler_parser.set_defaults(func=_tiddlywiki_exec)

view_parser = subparsers.add_parser('view', help='View entries on command line')
def parse_date(sdate):
    if sdate.lower() == 'today':
        return date.today()
    if sdate.lower() == 'yesterday':
        return date.today()-timedelta(days=1)
    if sdate.lower() == 'lastyear':
        t = date.today()
        return date(t.year-1, t.month, t.day)
    return datetime.strptime(sdate, '%Y-%m-%d').date()
view_parser.add_argument('date', type=parse_date)
def _view_exec(args):
    view(Diary.discover_and_load(diary_path), args.date)
view_parser.set_defaults(func=_view_exec)

def main():
    try:
        args = parser.parse_args()
        args.func(args)
    except Exception as e:
        import sys, traceback
        tb = sys.exc_info()[2]
        RED = ''
        try:
            import colorama
            colorama.init(autoreset=True)
            RED = colorama.Back.RED
        except ImportError:
            pass
        traceback.print_tb(tb)
        print(RED + type(e).__name__ + ': ' + str(e))