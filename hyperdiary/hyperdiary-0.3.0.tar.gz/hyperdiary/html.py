import os,re
from datetime import date, timedelta
from itertools import groupby
from collections import defaultdict
from . import diary
from .simplepath import AbsolutePath, RelativePath
from .htmltags import *

def nice_date(dt):
    return dt.strftime("%d.%m.%Y")

def day_to_html(current, entry, link_to_id_fn=None):
    day = article(_class='card', _id=str(path_for_date(current)))(header(h4(nice_date(current))))
    day_list = day.subelement(ul())
    for e in entry:
        if isinstance(e, str):
            eli = li()
            if link_to_id_fn:
                tags_to_print = []
                for token in diary.tokenize(e):
                    if token.type == diary.TokenType.Id:
                        eli.append(a(token.text, href=link_to_id_fn(token.ref)))
                    elif token.type == diary.TokenType.Text:
                        eli.append(span(token.text))
                    elif token.type == diary.TokenType.Tag:
                        tags_to_print.append(token)
                    else:
                        raise NotImplementedError('Unknown TokenType')
                for tag in tags_to_print:
                    eli.append(' ')
                    eli.append(span(tag.text, _class='tag'))
            else:
                eli.append(e)
            day_list.append(eli)
        elif isinstance(e, dict):
            for k, v in e.items():
                l = li(k)
                day_list.append(l)
                if isinstance(v, dict):
                    v = ['{}: {}'.format(_k, _v) for _k, _v in v.items()]
                uul = ul()
                day_list.append(uul)
                for _l in v:
                    uul.append(li(str(_l)))
    return day

def wrap_html_page(content, title=None, level=0):
    return wrap_page(
        div(content, _class='content'),
        page_title = title,
        css_references = [('../'*level) + 'assets/css/picnic.min.css'],
        inline_css = '.content { max-width: 800px; margin: auto; font-family: lato, sans-serif;} .tag { background-color: #ffeeaa;}'
    )

def diary_to_html(diary, fname):
    entries = diary.entries

    content = div(h1('Entries'))
    entries_html = content.subelement(div())

    for current in sorted(entries.keys()):
        entries_html.append(day_to_html(current, entries[current], lambda ref: '#'))

    wrap_html_page(content, title='Diary').write(fname)

def diary_to_html_folder(diary_instance, folder):
    entries = diary_instance.entries
    dates = list(entries.keys())
    dates.sort()

    root_path = path('/')
    entries_path = path('/entries')
    ids_path = path('/ids')

    def folder_from_path(p: AbsolutePath):
        return os.path.join(folder, str(p - root_path))
    entries_ul = ul()

    identifiers = defaultdict(list)

    for year, dates in groupby(dates, lambda d: d.year):
        year_path = entries_path + path(year)
        year_ul = ul()

        for month, dates in groupby(dates, lambda d: d.month):
            s_month = '{:02d}'.format(month)
            month_path = year_path + path(s_month)
            month_html = div(h1('{} {}'.format(MONTH_NAMES[month-1], year)))
            month_ul = month_html.subelement(ul())

            for current in dates:
                s_day = '{:02d}'.format(current.day)
                day_path = month_path + path(s_day)
                day_folder = folder_from_path(day_path)
                os.makedirs(day_folder, exist_ok=True)
                day_html = day_to_html(current, entries[current], lambda sid: str(ids_path + path(sid) - day_path))

                foot = div(_class='flex four')
                day_html.append(footer(foot))
                yesterday = current - timedelta(days=1)
                foot.append( div(a('Yesterday ({})'.format(yesterday), href=str(path_for_date(yesterday) - day_path))) )

                tomorrow = current + timedelta(days=1)
                foot.append( div(a('Tomorrow ({})'.format(tomorrow), href=str(path_for_date(tomorrow) - day_path)), _class='off-fourth') )

                wrap_html_page(day_html, level=4).write(os.path.join(day_folder, 'index.html'))
                append_li_a(month_ul, str(current), str(day_path - month_path))

                for dt, e, tp in diary.iter_entries({current: entries[current]}):
                    if tp == diary.EntryType.Line:
                        for identifier in diary.find_ids(e):
                            identifiers[identifier].append(dt)

            wrap_html_page(month_html, level=3).write(os.path.join(folder_from_path(month_path), 'index.html'))
            append_li_a(year_ul, MONTH_NAMES[month-1], s_month)

        wrap_html_page(year_ul, level=2).write(os.path.join(folder_from_path(year_path), 'index.html'))
        append_li_a(entries_ul, str(year), str(year))

    wrap_html_page(entries_ul, level=1).write(os.path.join(folder_from_path(entries_path), 'index.html'))

    ids_ul = ul()
    for identifier, days in sorted(identifiers.items()):
        id_path = ids_path + path(identifier.ref)
        id_folder = folder_from_path(id_path)
        os.makedirs(id_folder, exist_ok=True)
        append_li_a(ids_ul, identifier.text, str(id_path - ids_path))
        identifier_ul = ul()
        for day in days:
            append_li_a(identifier_ul, str(day), str(path_for_date(day) - id_path))
        wrap_html_page(identifier_ul, level=2).write(os.path.join(id_folder, 'index.html'))
    wrap_html_page(ids_ul, level=1).write(os.path.join(folder_from_path(ids_path), 'index.html'))
    import shutil
    shutil.rmtree(os.path.join(folder, 'assets'), ignore_errors=True)
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'assets'), os.path.join(folder, 'assets'))

MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', \
'July', 'August', 'September', 'October', 'November', 'December']

def path(spath):
    spath = str(spath)
    return AbsolutePath(spath) if spath.startswith('/') else RelativePath(spath)

def path_for_date(date):
    return path('/entries/{}/{:02d}/{:02d}'.format(date.year, date.month, date.day))

def append_li_a(ul, text, href):
    ul.append(li(a(text, href=href)))
