from dateparser import parse as date_parse

from django.core.cache import cache
from django.forms import DateInput

from hashlib import md5


class NaturalDateInput(DateInput):
    def _parse_date(self, date_string):
        return date_parse(date_string)

    def value_from_datadict(self, data, files, name):
        date = data.get(name)

        if not date:
            return date

        hasher = md5()
        hasher.update(date.encode('utf-8'))
        cache_key = 'date_parse_{0}'.format(hasher.hexdigest())

        parsed_date = cache.get(cache_key)

        if not parsed_date:
            parsed_date = self._parse_date(date)
            cache.set(cache_key, parsed_date, None)

        if parsed_date is None:
            return date
        else:
            return parsed_date
