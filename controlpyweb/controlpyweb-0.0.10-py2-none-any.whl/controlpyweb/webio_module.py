from controlpyweb.errors import ControlPyWebAddressNotFoundError
from controlpyweb.reader_writer import ReaderWriter
import datetime


class WebIOModule(ReaderWriter):

    def __init__(self, url: str):
        super().__init__(url)
        all_members = [d for d in dir(self) if not d.startswith('__')]
        for member in all_members:
            try:
                attr = getattr(self, member)
                attr._reader_writer = self
            except AttributeError:
                pass

    def _read_safe(self, addr: str):
        try:
            return self.read(addr)
        except ControlPyWebAddressNotFoundError:
            return None

    @property
    def serial_number(self) -> str:
        return self._read_safe("serialNumber")

    @property
    def vin(self) -> float:
        response = self._read_safe("vin")
        if response is None:
            return -1
        return float(response)

    @property
    def time_of_read(self):
        response = self._read_safe("utcTime")
        if response is None:
            return datetime.datetime.min
        return datetime.datetime.fromtimestamp(int(response))




