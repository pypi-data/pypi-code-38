import statistics

from auto_extract.language import get_language
import justext

import lxml.html
from metadate import parse_date

lang_to_stoplist = {"nl": justext.get_stoplist("Dutch"), "en": justext.get_stoplist("English")}

# TODO: https://www.evmi.nl/mensen-en-bedrijven/nieuwe-nederlander-koopt-vaker-a-merken-en-biologisch/
# after text, if date, that's a cutoff


def edge_distance(i, lower, upper):
    return min(abs(lower - i), abs(upper - i))


def different(text, title, date_str, simple=True):
    if not simple:
        from pyxdameraulevenshtein import damerau_levenshtein_distance

        return (
            damerau_levenshtein_distance(text, title) > 3
            and damerau_levenshtein_distance(text, date_str) > 3
        )
    text = text.strip()
    title = title.strip()
    date_str.strip()
    return text != title and text != date_str


def get_content(response_body, title, language, url):
    language = language if language in lang_to_stoplist else "en"
    stoplist = lang_to_stoplist[language]
    good_inds = []

    tree = lxml.html.fromstring(response_body)
    texts = justext.justext(response_body, stoplist)

    for line_num, x in enumerate(texts):
        x.num_ = line_num
        if not x.is_boilerplate or x.is_heading:
            good_inds.append(line_num)
        # print(x.is_boilerplate, x.text)

    # might need to take the center and then count outwards
    # center = statistics.median(good_inds)
    date = None
    body = None
    date_text = None
    # try on url
    md = parse_date(url)
    if md is not None and md.is_publish_date:
        date = md.start_date
        date_text = md.text[0]

    if good_inds:
        if date_text is None:
            lower_index, upper_index = good_inds[0], good_inds[-1]
            date_candidates = sorted(
                range(len(texts)), key=lambda x: edge_distance(x, lower_index, upper_index)
            )
            date_candidates = [texts[i] for i in date_candidates]
            date_candidates = [x for x in date_candidates if len(x) < 100]
            for x in date_candidates:
                md = parse_date(x.text, lang=language)
                if md is None:
                    continue
                # add some logic for element <time> or so
                if md.is_publish_date:
                    # in case someone writes english dates in other langs
                    if language != "en":
                        emd = parse_date(x.text)
                        if emd is not None and emd.min_level < md.min_level:
                            md = emd
                    date = md.start_date
                    date_text = x.text
                    break
        date_text = date_text or "NOTGONNAMATCH"

        texts = [texts[x] for x in good_inds]
        first_ind = min(good_inds)
        body = "\n".join(
            [
                x.text
                for x in texts
                if not x.is_boilerplate
                and x.num_ > first_ind
                and different(x.text, title, date_text)
            ]
        )

    return date, body
