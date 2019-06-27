from typing import Any, List, Union

from django.db.models import Q, QuerySet
from validate_it import schema, Options


@schema
class Context:
    request: Any
    queryset: Any

    order: dict = Options(default=dict)

    user_filter: dict = Options(default=dict)
    user_exclude: dict = Options(default=dict)

    system_filter: Union[dict, Q, None] = Options(default=None)
    system_exclude: Union[dict, Q, None] = Options(default=None)

    merged_filter: Union[dict, Q, None] = Options(default=None)
    merged_exclude: Union[dict, Q, None] = Options(default=None)

    project: List[str] = Options(default=list)
    items: Union[List[dict], QuerySet] = Options(default=list)
    meta: dict = Options(default=dict)
    status_code: int = Options(default=0)

    limit: int = Options(default=0)
    skip: int = Options(default=0)

    total: int = Options(default=0)
    created: int = Options(default=0)
    updated: int = Options(default=0)
    deleted: int = Options(default=0)
