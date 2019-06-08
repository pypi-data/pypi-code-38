"""Contains data classes that specify how a book is put together"""

from ..qr.qr import QR
from attr import dataclass, Factory
from typing import List
from .book import Book


@dataclass
class Chapter:
    title: str = ''
    file_name: str = ''
    content: str = ''


@dataclass(slots=True)
class Hardback:
    sources: List[str] = Factory(list)
    book: Book = Factory(Book)
    dimensions: List[int] = Factory(lambda: [5, 7])
    outfile: str = ''
    qr: QR = Factory(QR)

    options: dict = Factory(dict)
    progress_bar: bool = True
    remove_image_files: bool = True
    qr_image_dir: str = '.output'
