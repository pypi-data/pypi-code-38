
import csv
from io import TextIOWrapper
from os import PathLike
from pkg_resources import resource_stream


class Register:

    __metadata_keys__ = [
        "index-entry-number",
        "entry-number",
        "entry-timestamp",
        "key",
    ]

    def find(self, key):
        """Find a record using the register key"""

        return self.data[key]["item"]

    @classmethod
    def read_csv(cls, csvfile, metadata_keys=None):
        if metadata_keys is None:
            metadata_keys = cls.__metadata_keys__

        for entry in csv.DictReader(csvfile):
            key = entry["key"]
            metadata = {k: v for k, v in entry.items() if k in metadata_keys and v}
            item = {k: v for k, v in entry.items() if k not in metadata_keys and v}
            new_entry = metadata.copy()
            new_entry["item"] = item.copy()
            yield (key, new_entry)

    @classmethod
    def from_csv(cls, csvfile):
        """Create a register object from a CSV file

        :param csvfile:  CSV file path or stream
        :type csvfile: os.PathLike or file object
        """

        if isinstance(csvfile, (str, PathLike)):
            with open(csvfile, newline="", encoding="utf-8") as f:
                data = dict(cls.read_csv(f))
        else:
            data = dict(cls.read_csv(csvfile))

        register = cls.__new__(cls)
        register.data = data

        return register

    @classmethod
    def from_pkg_resource(cls, csvfile, pkg=__name__):
        """Create a register object from a CSV file
        that is included with a package

        :param csvfile str: CSV file name
        :param pkg str: package name (defaults to this package)
        """

        f = TextIOWrapper(resource_stream(pkg, csvfile), encoding="utf-8")
        return cls.from_csv(f)
