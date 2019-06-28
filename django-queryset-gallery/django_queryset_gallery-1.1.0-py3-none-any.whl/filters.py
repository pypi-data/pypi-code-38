import abc
from django.db.models import Q


class Filter(abc.ABC):
    """Use for creating filter classes

    Args:
        `key` (str): the unique filter identification

    Methods:
        `apply`: apply filter for objects
        `apply_from_dict_params`: the same as `apply` but get filter param from params dict
    """
    def __init__(self, key):
        self.key = key

    def apply(self, objects, param):
        return self._execute(objects, param)

    def apply_from_dict_params(self, objects, params: dict):
        if self.key in params:
            objects = self._execute(objects, params[self.key])
        return objects

    @abc.abstractmethod
    def _execute(self, objects, param):
        return objects


class QuerySetFilter(Filter):
    """Base on lookup queryset filtering

    Args:
        `key` (str): the same as in Filter
        `lookup` (str): lookup for filtering. Example "user__email"

    Usage:
        ```
        UserEmailFilter = QuerySetFilter('is_active', 'user_is_active')
        users = UserEmailFilter.apply(users, 'True')
        ```
    """
    def __init__(self, key, lookup):
        super().__init__(key)
        self.lookup = lookup

    def _execute(self, queryset, param):
        return queryset.filter(**{self.lookup: param})


class QuerySetSimpleSearch(Filter):
    """The same as QuerySetFilter but get several lookups and filter via OR

    Args:
        `key` (str): the same as in Filter
        `lookups` (list): lookups for filtering, like ["user__first_name", "user__last_name"]

    Usage:
        ```
        UserSearch = QuerySetSearch(
            key='query',
            lookups=["user__first_name", "user__last_name"]
        )
        users = UserSearch.apply(users, ['Liza', 'Alex'])
        ```
    Note:
        Get param as list, not a string
    """
    def __init__(self, key, lookups):
        super().__init__(key)
        self.lookups = lookups

    def _get_q_object(self, params: list):
        q = Q()
        for lp in self.lookups:
            for p in params:
                q |= Q(**{lp: p})
        return q

    def _execute(self, queryset, param):
        assert isinstance(param, list), f"The param must be a list, not a {type(param)}"
        q = self._get_q_object(params=param)
        return queryset.filter(q)
