class FieldsetError(Exception):
    pass


class Fieldset:
    def __init__(self, field=None, refsets=None):
        self._values = None
        self.field = field
        self._refsets = refsets
        self._filter_values = None
        self.all()

    def __repr__(self):
        return f"{self.__class__.__name__}(field={self.field}, refsets={self._refsets})"

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, i):
        return self._values[i]

    def __len__(self):
        return len(self._values)

    @property
    def values(self):
        return self._values

    def all(self):
        self._values = [getattr(t, self.field) for t in self._refsets]
        return self

    def filter(self, *values):
        if len(values) > 0:
            self._values = [v for v in self._values if v in values]
            self._filter_values = values
        return self

    def order_by(self, field=None):
        """Re-order the collection ref objects by a single field
        and rebuild the values list.
        """
        field = field or "report_datetime"
        self.ordering = field
        reverse = False
        if field.startswith("-"):
            field = field[1:]
            reverse = True
        try:
            getattr(self._refsets[0], field)
        except AttributeError as e:
            raise FieldsetError(f"Invalid ordering field. field={field}. Got {e}")
        except IndexError:
            pass
        else:
            self._refsets.sort(key=lambda x: getattr(x, field) or 0, reverse=reverse)
        self.all()
        if self._filter_values:
            self.filter(*self._filter_values)
        return self

    def first(self, value=None):
        """Returns the first value from the list of values.

        Excludes None.
        """
        if value:
            values = [v for v in self._values if v == value]
        else:
            values = [v for v in self._values if v is not None]
        try:
            return values[0]
        except IndexError:
            return None

    def last(self, value=None):
        """Returns the last value from the list of values.

        Excludes None.
        """
        if value:
            values = [v for v in self.values if v == value][-1:]
        else:
            values = [v for v in self._values if v is not None][-1:]
            # values = self.values[-1:]
        try:
            return values[0]
        except IndexError:
            return None
