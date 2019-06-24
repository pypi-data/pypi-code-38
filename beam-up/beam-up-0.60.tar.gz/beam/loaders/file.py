from .base import BaseLoader

class FileLoader(BaseLoader):

    def __init__(self, site):
        super().__init__()
        self.site = site

    def load(self, path):
        abs_path = self.site.get_src_path(path)
        with open(abs_path) as input_file:
            return input_file.read()
