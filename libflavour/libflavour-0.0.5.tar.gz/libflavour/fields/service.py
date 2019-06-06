import attr
from strictyaml import Bool, Int, Map, Optional, Str

from .base import BaseField


@attr.s
class DatabaseField(BaseField):
    identifier = "service/database"

    def __str__(self):
        return f"{self.label} - database - {self.visibility} "

    @classmethod
    def additional_schema(cls):
        return {Optional("default"): Bool()}
