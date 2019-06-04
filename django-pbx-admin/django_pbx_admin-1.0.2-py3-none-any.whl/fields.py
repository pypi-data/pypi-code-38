from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Lookup


class AsTextTransform(models.Transform):
    """Text transform lookup for JSONField.

    Usage: filter(shinar_name__en__as_text__icontains='bleble')
    """

    lookup_name = "as_text"

    def as_sql(self, qn, connection):
        lhs, params = qn.compile(self.lhs)
        splited = lhs.split("->")
        lhs = "->>".join(["->".join(splited[:-1]), splited[-1]])
        return "CAST(%s as %s)" % (lhs, "text"), params

    @property
    def output_field(self):
        return models.CharField()


JSONField.register_lookup(AsTextTransform)


# Ltree field


class LtreeField(models.CharField):
    description = "ltree (up to %(max_length)s)"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 256
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return "ltree"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs


class AncestorOrEqual(Lookup):
    lookup_name = "aore"

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "%s @> %s" % (lhs, rhs), params


LtreeField.register_lookup(AncestorOrEqual)


class DescendantOrEqual(Lookup):
    lookup_name = "dore"

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "%s <@ %s" % (lhs, rhs), params


LtreeField.register_lookup(DescendantOrEqual)


class Match(Lookup):
    lookup_name = "match"

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "%s ~ %s" % (lhs, rhs), params


LtreeField.register_lookup(Match)
