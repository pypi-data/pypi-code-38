import base64
import csv
import os
from collections import defaultdict


class State(defaultdict):
    field_names = ["migration_name", "migration_hash", "migration_forced"]

    def __init__(self, cache_path):
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        self.cache_path = cache_path
        super().__init__(dict)

    def load(self):
        self.clear()
        for file_name in os.listdir(self.cache_path):
            file_path = os.path.join(self.cache_path, file_name)
            if os.path.isfile(file_path):
                rows = []
                with open(file_path, "r") as csv_file:
                    reader = csv.DictReader(csv_file, fieldnames=self.field_names)
                    for row in reader:
                        rows.append(row)
                self[file_name] = {row["migration_name"]: row for row in rows}

    def save(self):
        for key in self:
            with open(os.path.join(self.cache_path, key), "w") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.field_names)
                for row in sorted(
                    self[key].values(), key=lambda m: m["migration_name"]
                ):
                    writer.writerow(row)
