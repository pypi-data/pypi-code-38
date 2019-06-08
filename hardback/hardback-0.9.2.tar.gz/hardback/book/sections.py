from .chunk_writer import write_chunks
from .metadata import format as metadata_format
from ..qr import qr_table
from ..util import chunk_sequence
from ebooklib import epub
from pathlib import Path


def chapter(hc):
    name = Path(hc.source).name
    return epub.EpubHtml(
        title=f'Metadata {name}',
        file_name=f'full_chapter_{hc.index}.xhtml',
        content=metadata_html(hc) + qr_html(hc),
    )


def qr(hc):
    return epub.EpubHtml(
        title=hc.source,
        file_name=f'qr-codes-{hc.index}.xhtml',
        content=qr_html(hc),
    )


def metadata(hc):
    item = epub.EpubHtml(
        title=hc.source,
        file_name=f'metadata_chapter_{hc.index}.xhtml',
        content=metadata_html(hc),
    )
    item.add_item(hc.hardback.book.default_css)
    return item


def qr_html(hc):
    def qr_code_images():
        chunks = write_chunks(hc)
        for block_count, f in enumerate(chunks):
            f = Path(f)
            add_image_item(f)
            hc.hardback.desc.remove_image_files and f.unlink()
            hc.hardback.bar.next_item(f.name)
            yield f.name

    def add_image_item(path):
        result = path.read_bytes()
        item = epub.EpubItem(file_name=path.name, content=result)
        hc.hardback.book.add_item(item)

    c, r = hc.hardback.desc.dimensions
    images = qr_code_images()
    chunks = chunk_sequence.chunk_sequence(images, c, r)
    return '\n'.join(qr_table.qr_table(chunks, c, r))


def metadata_html(hc):
    return metadata_format(index=hc.index, **hc.metadata)
