""" Provides csv-file implementation of Subject Mapping """
import collections
import csv
import json
import logging

from copy import copy

from .subject_map import SubjectMap, SubjectMapConfig, SUBJECT_CODE_KEY

log = logging.getLogger(__name__)

CONFIG_KEY = '$config'


class CSVSubjectMap(SubjectMap):
    """CSV based subject mapping. Keys are an ordered tuple of key, value pairs.

    In addition, records are kept in the same order in the file.
    """
    def __init__(self, path):
        super(CSVSubjectMap, self).__init__()
        self.path = path
        self.last_id = 0
        self.idmap = collections.OrderedDict()

    def lookup_code(self, record):
        # Create the key map
        key = tuple([(field, self.extract_field(record, field)) for field in self.config.fields])
        # Check if key is in the id map already
        code = self.idmap.get(key)
        if code is None:
            # Increment the last id, and add it to the map
            code = self.last_id + 1
            self.last_id = code
            self.idmap[key] = code
        return code

    def load(self):
        with open(self.path, 'r') as f:
            first = True
            reader = csv.DictReader(f)
            for row in reader:
                # Read settings from first row
                if first:
                    self._read_config(reader.fieldnames, row)
                    first = False
                    continue
                # Otherwise load rows into idmap
                self._read_row(row)

    def save(self):
        with open(self.path, 'w') as f:
            fieldnames = copy(self.config.fields) + [SUBJECT_CODE_KEY, CONFIG_KEY]
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()

            # Write config
            config_str = json.dumps({'format': self.config.format_str})
            writer.writerow({CONFIG_KEY: config_str})

            # Write remaining rows
            for row in self.rows():
                writer.writerow(row)

    def rows(self):
        for key, code in self.idmap.items():
            yield collections.OrderedDict(key + ((SUBJECT_CODE_KEY, code),))

    def _read_config(self, fieldnames, row):
        """ Read config from the first row of the CSV file """
        # Copy fieldnames
        fieldnames = list(fieldnames)
        fieldnames.remove(CONFIG_KEY)
        fieldnames.remove(SUBJECT_CODE_KEY)

        # Load config json
        config = None
        config_value = row.get(CONFIG_KEY, '')
        try:
            config = json.loads(config_value)
        except ValueError:
            log.exception('Unable to load config')

        # Verify the result
        if not config or not config.get('format'):
            raise ValueError('Subject map does not include configuration!')

        self.config = SubjectMapConfig(fieldnames, config['format'])

    def _read_row(self, row):
        """ Read a single row from the CSV file """
        key = tuple([(fieldname, row[fieldname]) for fieldname in self.config.fields])
        code = int(row[SUBJECT_CODE_KEY])
        self.idmap[key] = code
        if code > self.last_id:
            self.last_id = code

    @staticmethod
    def create(path, config):
        """Create a new CSV subject map with config, and save it at path

        Args:
            path (str): The path of the subject map file
            config (SubjectMapConfig): The configuration to use

        Returns:
            SubjectMap: The CSV subject map instance
        """
        result = CSVSubjectMap(path)
        result.config = config
        result.save()
        return result
