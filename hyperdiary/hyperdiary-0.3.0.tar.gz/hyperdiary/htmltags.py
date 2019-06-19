_escaped_attrs = ('id', 'class', 'type')
_html_tags = ('html', 'head', 'title', 'meta', 'link', 'style', \
              'body', 'div', 'nav', 'span', 'article', 'header', 'footer', 'a', 'p', \
              'h1', 'h2', 'h3', 'h4', \
              'small', 'hr', 'ul', 'ol', 'li', 'img', \
              'table', 'thead', 'tbody', 'tr', 'td', 'th', \
              'form', 'button')
_render_compact_tags = ('p', 'span', 'a', 'b', 'i', 'small', 'li', \
                        'h1', 'h2', 'h3', 'h4', \
                        'button', 'ht', 'td', 'title')

class HTMLElement(object):
    tag = 'div'

    def __init__(self, *content, **attributes):
        self.content = list(content)
        self.attributes = attributes
        for a in _escaped_attrs:
            if '_' + a in self.attributes:
                self.attributes[a] = self.attributes.pop('_' + a)

    def append(self, *items):
        self.content += items
        return self

    def __call__(self, *items):
        return self.append(*items)

    def subelement(self, item):
        self.content.append(item)
        return item

    def lazy_render_attributes(self):
        if self.attributes:
            for k, v in self.attributes.items():
                yield ' '
                yield str(k)
                yield '="'
                yield str(v)
                yield '"'

    def lazy_render(self, indent='', add_indent=''):
        is_doc_root = self.tag.lower() == 'html'
        if is_doc_root:
            yield '<!DOCTYPE HTML>\n'
        do_linebreak = not self.tag in _render_compact_tags and self.content
        yield indent
        yield '<'
        yield self.tag
        yield from self.lazy_render_attributes()
        yield '>'
        if do_linebreak:
            yield '\n'
        child_indent = indent + add_indent if do_linebreak else ''
        if not do_linebreak:
            add_indent = ''
        for child in self.content:
            if hasattr(child, 'lazy_render'):
                yield from child.lazy_render(child_indent, add_indent)
            else:
                yield '{}{}'.format(child_indent, child)
            if do_linebreak:
                yield '\n'
        if do_linebreak:
            yield indent
        yield '</'
        yield self.tag
        yield '>'
        if is_doc_root:
            yield '\n'

    def __str__(self):
        return ''.join(self.lazy_render(add_indent='  '))

    def write(self, fname):
        with open(fname, 'w') as f:
            for s in self.lazy_render(add_indent='  '):
                f.write(s)

for tag in _html_tags:
    locals()[tag.lower()] = type(tag.lower(), (HTMLElement,), dict(tag=tag))

def wrap_page(body_content, page_title=None, encoding='utf-8', css_references=[], inline_css=None):
    h = head(
            meta(charset=encoding),
            meta(name='viewport', content='width=device-width, initial-scale=1')
        )
    if page_title:
        h.append(title(page_title))
    for css in css_references:
        h.append(link(href=css, rel="stylesheet"))
    if inline_css:
        h.append(style(inline_css))
    return html(h, body(body_content))

mycss = \
"""body {
  padding-top: 60px;
}"""
if __name__ == '__main__':
    content = div(
            p('Hello World'),
            'asdasd',
            a('asd', href='#'),
            p(
                span('hi'),
                a('asd', href='#'),
                span('there')
            ),
            div(div(p('hello')), 'text', span('world'))
        )
    page = wrap_page(content, page_title='My test page', css_references=["assets/css/bootstrap.min.css"], inline_css=mycss)
    print(page)
