from ms_sdk.Lib.Filters.FilterOperators import FilterOperators
from ms_sdk.Lib.Filters.FilterConditions import FilterConditions


class Filter(FilterOperators, FilterConditions):

    availableFilters = {
        FilterOperators.LIKE,
        FilterOperators.LIKE_LEFT,
        FilterOperators.LIKE_RIGHT,
        FilterOperators.EQUAL,
        FilterOperators.NOT_EQUAL,
        FilterOperators.GREATER_THAN,
        FilterOperators.LESS_THAN,
        FilterOperators.GREATER_THAN_OR_EQUAL,
        FilterOperators.LESS_THAN_OR_EQUAL,
        FilterOperators.IS_NULL
    }

    filters = {}

    def __init__(self, filters: dict = {}):
        """
        :param filters:
        """
        if filters:
            self.setFilters(filters)

    def getFilters(self):
        """
        Get the filter array
        :rtype dict:
        """
        return self.filters

    def setFilters(self, filters: dict):
        """
        :param filters: dict
        :rtype self:
        """
        self.filters = {}

        for field, rules in filters.items():
            if field == 'fullSearch':
                self.addFilter(field, rules, None)
                continue

            for operator, value in rules.items():
                if (not operator in self.availableFilters) or (
                        (not value) and value != '0'):
                    continue
                self.addFilter(field, value, operator)
        return self

    def addFilter(self, field, value, operator):
        """
        Adds a filter to the resource request
        :param field: the field to filter on
        :param value: the value of the attribute to operate on
        :param operator: the filter operator (eq,ne etc)
        :rtype self:
        """
        if field and (value or value == '0'):
            if operator:
                self.filters[field] = {}
                self.filters[field].update({operator : str(value)})
            else:
                self.filters[field] = value
        return self

    def toString(self):
        """
        Convert the filter object to a string for a URL
        :rtype: str
        :rtype str:
        """
        if len(self.filters) > 1:
            filters = '[' + \
                      str(self.filters)\
                          .replace("'", '"')\
                          .replace(' :', ':')\
                          .replace(': ', ':')\
                          .replace(', ', '}, {')\
                      + ']'
        else:
            filters = str(self.filters)\
                .replace("'", '"')\
                .replace(' :', ':')\
                .replace(': ', ':')
        return filters
