from io import BytesIO

from tabulator.loader import Loader


class BytesLoader(Loader):
    """Custom loader for bytes string"""

    def __init__(self, bytes_sample_size, **options):
        pass

    def load(self, source, mode, encoding=None):
        return BytesIO(source)


custom_loaders = {"bytes": BytesLoader}
