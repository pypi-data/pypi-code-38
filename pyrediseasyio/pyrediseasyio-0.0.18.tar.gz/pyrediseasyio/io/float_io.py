from pyrediseasyio import SingleIO
from pyrediseasyio.abstract_reader_writer import AbstractReaderWriter


class FloatIO(SingleIO):
    def __init__(self, name: str, addr: str = None, default: float = 0, units: str = None, reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, units, reader)

    @staticmethod
    def _convert_type(value):
        return float(value)


