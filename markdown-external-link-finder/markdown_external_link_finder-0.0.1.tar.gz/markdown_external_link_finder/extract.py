import mistune
from .util import LinkRenderer

def extract_markdown_links(markdown_files):
    impl = LinkRenderer()
    renderer = mistune.Markdown(renderer=impl)

    for markdown_file in markdown_files:
        with open(markdown_file) as f:
            text = f.read()
        renderer(text)

    yield from impl.urls