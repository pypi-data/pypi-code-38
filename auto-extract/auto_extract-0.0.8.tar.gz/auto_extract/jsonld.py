import re
import html
import lxml.html
import ujson as json

HTML_OR_JS_COMMENTLINE = re.compile(r'^\s*(//.*|<!--.*-->)')


def extract_jsonld(tree):
    results = []
    for script in tree.xpath('//script[@type="application/ld+json"]/text()'):
        try:
            # TODO: `strict=False` can be configurable if needed
            data = json.loads(script)
        except ValueError:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            try:
                data = json.loads(HTML_OR_JS_COMMENTLINE.sub('', script))
            except ValueError:
                import json as j

                try:
                    data = j.loads(script)
                except j.JSONDecodeError:
                    data = j.loads(html.unescape(script.replace("\\'", "'")))
        results.append(data)
    return results
