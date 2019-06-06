
import csv
from os import PathLike

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

    @staticmethod
    def read_csv(csvfile, metadata_keys):
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
                data = dict(cls.read_csv(f, metadata_keys=cls.__metadata_keys__))
        else:
            data = dict(cls.read_csv(csvfile, metadata_keys=cls.__metadata_keys__))

        register = cls.__new__(cls)
        register.data = data

        return register
