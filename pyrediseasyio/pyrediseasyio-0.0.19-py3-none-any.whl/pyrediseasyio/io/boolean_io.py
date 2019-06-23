from pyrediseasyio import SingleIO
from pyrediseasyio.abstract_reader_writer import AbstractReaderWriter
from str2bool import str2bool


class BooleanIO(SingleIO):
    def __init__(self, name: str, addr: str = None, default: bool = False, units: str = None,
                 reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, units, reader)

    @staticmethod
    def _convert_type(value):
        if value is None:
            return False
        if isinstance(value, str):
            return str2bool(value)
        return bool(value)

    def __bool__(self):
        return self.value

    @property
    def value(self) -> bool:
        return super().value
