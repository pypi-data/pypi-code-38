from .book import cursor, hardback, sections
from .data import serialize, dataclass
import pathlib
import yaml

_DATA_SUFFIXES = '.json', '.yml'
NEW_CHAPTERS = False


def main(files):
    desc = dataclass.Hardback()
    for f in files:
        if pathlib.Path(f).suffix in _DATA_SUFFIXES:
            serialize.unserialize(f, desc)
        else:
            desc.sources.append(f)

    hb = hardback.Hardback(desc)

    print(yaml.dump(serialize.serialize(hb.desc)))

    for hc in cursor.HardbackCursor(hb):
        hb.book.toc.extend((sections.metadata(hc), sections.qr(hc)))

    hb.add_items(*hb.book.toc)
    hb.write()


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
