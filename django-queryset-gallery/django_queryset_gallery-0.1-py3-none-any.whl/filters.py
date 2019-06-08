import abc


class Filter(abc.ABC):
    """Use for creating filter classes

    Args:
        `filter_key` (str): the unique filter identification

    Methods:
        `apply`: apply filter for objects
        `apply_dict_params`: the same as `apply` but get filter param from params dict
    """
    filter_key = ''

    def apply(self, objects, param):
        return self._execute(objects, param)

    def apply_dict_params(self, objects, params: dict):
        if self.filter_key in params:
            objects = self._execute(objects, params[self.filter_key])
        return objects

    @abc.abstractmethod
    def _execute(self, objects, param):
        """Execute filter to objects and return objects"""
        return objects


class QuerySetFilter(Filter):
    """Base on lookup queryset filtering

    Args:
        `key` (str): the same as in Filter
        `lookup` (str): lookup for filtering. Example "user__email"

    Usage:
        ```
        UserEmailFilter = QuerySetFilter('user_is_active', 'user_is_active')
        users = UserEmailFilter.apply(users, 'True')
        ```
    """
    filter_key = ''
    lookup = ''

    def _execute(self, queryset, param):
        return queryset.filter(**{self.lookup: param})
