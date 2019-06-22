from pyrediseasyio.abstract_reader_writer import AbstractReaderWriter
from pyrediseasyio import SingleIO


class StringIO(SingleIO):
    def __init__(self, name: str, addr: str = None,
                 default: str = '', units: str = None, reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, units, reader)

    @staticmethod
    def _convert_type(value):
        return str(value)