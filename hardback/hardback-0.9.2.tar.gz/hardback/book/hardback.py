from .css import make_css
from . import metadata
from ..qr.fill import fill_qr
from ..util import hasher
from ..util.elapsed_bar import ElapsedBar
from ebooklib import epub
from pathlib import Path


class Hardback:
    def __init__(self, desc):
        if not desc.sources:
            raise ValueError('No filename')
        # Must be done first
        desc.book.fill(desc.sources)
        fill_qr(desc.qr)

        head = Path(desc.sources[0])
        desc.outfile = desc.outfile or head.stem + '.epub'

        self.desc = desc
        self.metadatas = [metadata.metadata(desc, s) for s in desc.sources]
        total_blocks = sum(m['block']['count'] for m in self.metadatas)

        if not desc.book.identifier:
            hashes = (m['sha256'].encode() for m in self.metadatas)
            d = hasher.hash_digest(hashes)
            desc.book.identifier = d.hexdigest()

        self.book = epub.EpubBook()

        desc.book.apply(self.book)
        self.book.default_css = make_css('default')
        self.add_items(self.book.default_css)
        self.bar = ElapsedBar(max=total_blocks, enable=desc.progress_bar)

    def add_items(self, *items):
        for i in items:
            self.book.add_item(i)

    def write(self):
        self.add_items(epub.EpubNcx(), epub.EpubNav(), make_css('nav'))
        self.book.spine = ['nav'] + self.book.toc
        epub.write_epub(self.desc.outfile, self.book, **self.desc.options)
