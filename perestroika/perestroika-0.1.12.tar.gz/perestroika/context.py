from typing import Any, List

import attr


@attr.s(auto_attribs=True)
class Context:
    request: Any
    queryset: Any

    order: dict
    filter: dict
    exclude: dict
    project: List[str]
    items: List[dict]
    meta: dict
    status_code: int = attr.ib(default=0)

    limit: int = attr.ib(default=0)
    skip: int = attr.ib(default=0)

    total: int = attr.ib(default=0)
    created: int = attr.ib(default=0)
    updated: int = attr.ib(default=0)
    deleted: int = attr.ib(default=0)
