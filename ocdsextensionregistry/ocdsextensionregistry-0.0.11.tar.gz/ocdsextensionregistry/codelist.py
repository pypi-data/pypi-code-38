from collections import OrderedDict

from .codelist_code import CodelistCode


class Codelist:
    def __init__(self, name):
        self.name = name
        self.rows = []

    def __getitem__(self, index):
        return self.rows[index]

    def __iter__(self):
        for row in self.rows:
            yield row

    def __len__(self):
        return len(self.rows)

    def __repr__(self):
        return 'Codelist(name={}, rows={})'.format(repr(self.name), repr(self.rows))

    def extend(self, rows, extension_name=None):
        """
        Adds rows to the codelist.
        """
        for row in rows:
            self.rows.append(CodelistCode(row, extension_name))

    def add_extension_column(self, field_name):
        """
        Adds a column for the name of the extension from which codes originate.
        """
        for row in self.rows:
            row[field_name] = row.extension_name

    def remove_deprecated_codes(self):
        """
        Removes deprecated codes and the Deprecated column.
        """
        self.rows = [row for row in self.rows if not row.pop('Deprecated', None)]

    @property
    def codes(self):
        """
        Returns the codes in the codelist.
        """
        return [row['Code'] for row in self.rows]

    @property
    def fieldnames(self):
        """
        Returns all fieldnames used in any rows.
        """
        fieldnames = OrderedDict()
        for row in self.rows:
            for field in row:
                fieldnames[field] = True
        return list(fieldnames.keys())

    @property
    def basename(self):
        """
        If the codelist modifies another codelist, returns the latter's name. Otherwise, returns its own name.
        """
        if self.patch:
            return self.name[1:]
        return self.name

    @property
    def patch(self):
        """
        Returns whether the codelist modifies another codelist.
        """
        return self.name.startswith(('+', '-'))

    @property
    def addend(self):
        """
        Returns whether the codelist adds codes to another codelist.
        """
        return self.name.startswith('+')

    @property
    def subtrahend(self):
        """
        Returns whether the codelist removes codes from another codelist.
        """
        return self.name.startswith('-')
