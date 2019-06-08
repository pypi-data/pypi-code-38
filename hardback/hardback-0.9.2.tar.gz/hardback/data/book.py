from attr import dataclass, Factory
from pathlib import Path
from typing import List


@dataclass(slots=True)
class Book:
    identifier: str = ''
    title: str = ''
    cover: str = ''
    language: str = 'en'
    authors: List[str] = Factory(list)

    def apply(self, ebook):
        ebook.set_identifier(self.identifier)
        ebook.set_title(self.title)
        ebook.set_language(self.language)

        for a in self.authors:
            ebook.add_author(a)

        if self.cover:
            with open(self.cover, 'rb') as fp:
                filename = 'cover_' + Path(self.cover).name
                ebook.set_cover(filename, fp.read())

    def fill(self, sources):
        if not self.cover:
            p = [i for i in sources if Path(i).suffix in SUFFIXES]
            self.cover = p and p[0]

        head = Path(sources[0])
        if not self.title:
            self.title = head.name
            if len(sources) > 1:
                self.title += ', ...'


SUFFIXES = '.jpeg', '.jpg', '.png'
