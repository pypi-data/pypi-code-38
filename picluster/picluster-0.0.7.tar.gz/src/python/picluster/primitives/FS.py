from pathlib import Path
from .base import maybe_type


class Url:
    def __init__(self, url):
        self.url = maybe_type(url, Path)

    def __str__(self):
        return str(self.url)

    def __repr__(self):
        return f"""{self.__class__.__name__}("{str(self.url)}")"""

    def to_path(self):
        return Path(str(self))


class File(Url):
    def __init__(self, url):
        super().__init__(url)
        if self.to_path().is_file():
            return
        else:
            raise ValueError(f"""VALUE ERROR ! Input url is not a file.""")


class Directory(Url):
    def __init__(self, url):
        super().__init__(url)
        if self.to_path().is_dir():
            return
        else:
            raise ValueError(
                f"""VALUE ERROR ! Input url is not a directory, or directory note exist."""
            )
