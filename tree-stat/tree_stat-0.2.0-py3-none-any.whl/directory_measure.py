import logging
from collections import defaultdict
from pathlib import Path

log = logging.getLogger('tree_stat.dm')


class DirectoryMeasure:
    def __init__(self, files, path=None, parent=None):
        self.path = path
        self.parent = parent if parent is not None else path.parent
        self.__measures_by_file_type = defaultdict(FileTypeMeasure)

        for f in (Path(f) for f in files):
            ext = f.suffix
            file_size = path.joinpath(f).stat().st_size
            self.__measures_by_file_type[ext].volume += file_size
            self.__measures_by_file_type[ext].count += 1

    @property
    def measures_by_file_type(self):
        return sorted(self.__measures_by_file_type.items())

    @property
    def total(self):
        it = FileTypeMeasure()
        for v in self.__measures_by_file_type.values():
            it.volume += v.volume
            it.count += v.count
        return it

    def eat(self, child):
        for ext, v in child.__measures_by_file_type.items():
            self.__measures_by_file_type[ext].volume += v.volume
            self.__measures_by_file_type[ext].count += v.count

    def edible_clone(self):
        clone = DirectoryMeasure([], parent=self.path.parent)
        clone.eat(self)
        return clone

    def __repr__(self):
        return 'DirectoryMeasure({})' \
            .format(', '.join(['{v}={{{v}}}'
                              .format(v=v) for v in vars(self).keys()])) \
            .format(**vars(self))


class FileTypeMeasure:
    def __init__(self):
        self.volume = 0
        self.count = 0

    def __repr__(self):
        return 'FilesMeasure({})' \
            .format(', '.join(['{v}={{{v}}}'
                              .format(v=v) for v in vars(self).keys()])) \
            .format(**vars(self))
