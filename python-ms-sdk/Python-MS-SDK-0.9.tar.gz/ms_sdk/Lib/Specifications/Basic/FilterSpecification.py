from ms_sdk.Lib.Filters.FilterOperators import FilterOperators


class FilterSpecification:

    def asFilter(self):
        """
        :rtype dict:
        """
        return {'visible': {FilterOperators.EQUAL: 1}}