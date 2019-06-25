import json
import sys
import re
import itertools
import html
from collections import namedtuple
import mistune

Parsed = namedtuple("Parsed", "title, tags, content, images")
Title = namedtuple("Title", "title, tags")
Image = namedtuple("Image", "src, text")


class _CaputringRenderer:
    def __init__(self, renderer):
        self.renderer = renderer
        self.result = {
            "title": Title(title="", tags=[]),
            "images": [],
        }

    def __getattr__(self, name):
        attr = getattr(self.renderer, name)
        if callable(attr):
            setattr(self.renderer, name, attr)  # method cache
        return attr

    def header(self, text, level, *args, **kwargs):
        if level == 1 and not self.result["title"].title:
            self.result["title"] = parse_title(text)
        return self.renderer.header(text, level, *args, **kwargs)

    def image(self, src, title, text):
        self.result["images"].append(Image(src=src, text=text))
        return self.renderer.image(src, title, text)


_scanner = re.Scanner([
    (r"\[", "["),
    (r"\]", "]"),
    (r"[^\]\[]+", lambda s, m: m),
])


def parse_title(title: str, *, scanner: re.Scanner = _scanner) -> Title:
    r, rest = scanner.scan(title.strip().lstrip("#"))
    assert not rest

    itr = (line for line in r if line.strip())
    tags = []
    buf = []
    for tk in itr:
        if tk != "[":
            buf.append(tk)
            break

        tag = next(itr)
        buf.append(tag)
        tk = next(itr)
        if tk != "]":
            buf.append(tag)
            buf.append(tk)
            break

        buf.pop()
        tags.append(tag.strip())
    return Title(tags=tags, title="".join(itertools.chain(buf, itr)).strip())


def parse_article(text: str) -> Parsed:
    capturing = _CaputringRenderer(mistune.Renderer())
    m = mistune.Markdown(renderer=capturing)
    m.render(text)
    result = capturing.result

    title = html.unescape(result["title"].title)
    itr = iter(text.splitlines())

    # lstrip title
    buf = []
    title_found = False
    finding_limit = 5
    for line in itertools.islice(itr, finding_limit):
        if title in line:
            title_found = True
            break
        buf.append(line)

    # for section using === such as
    # <section title>
    # =============
    #
    # text body

    headbuf = [next(itr)]
    if not headbuf[0].strip("="):
        headbuf.pop()
    if title_found:
        content = "\n".join(itertools.chain(headbuf, itr)).strip()
    else:
        content = "\n".join(itertools.chain(buf, headbuf, itr)).strip()

    return Parsed(
        title=title,
        tags=result["title"].tags,
        images=result["images"],
        content=content,
    )


def dump(parsed: Parsed, out=sys.stdout) -> None:
    def default(o):
        if hasattr(o, "_asdict"):
            return o._asdict()
        raise TypeError(f"unexpected type {type(o)!r}")

    json.dump(parsed._asdict(), out, indent=2, ensure_ascii=False, default=default)
