import enum

__all__ = ['Criteria', 'Inclusion', 'StringExpressionFactory']


class Criteria(object):
    def __init__(self):
        self.inclusion_entries = set()
        self.criterion_entries = set()

    def add(self, **kwargs):
        if 'inclusion' in kwargs:
            self.inclusion_entries.add(kwargs['inclusion'])
        if 'criterion' in kwargs:
            self.criterion_entries.add(kwargs['criterion'])
        return self

    def get_criteria_params(self):
        params = dict()
        for criterion in self.criterion_entries:
            criterion.apply_expression(params)
        if self.inclusion_entries:
            self.__create_inclusions(params)
        return params

    def _get_inclusion_entries(self):
        return list(self.inclusion_entries)

    def __create_inclusions(self, params):
        self.__add_inclusion_entries(params)
        self.__add_inclusion_field_entries(params)

    def __add_inclusion_entries(self, params):
        params["include"] = ",".join(sorted(map(str, self.inclusion_entries)))

    def __add_inclusion_field_entries(self, params):
        for inclusion in self.inclusion_entries:
            inclusion.add_field_entries(params)


class Inclusion(object):
    def __init__(self, resource_name):
        self.resource_name = resource_name
        self.fields_entries = set()

    @staticmethod
    def resource(resource_name):
        return Inclusion(resource_name=resource_name)

    def fields(self, *args):
        self.fields_entries = self.fields_entries.union(map(FieldSelector, args))
        return self

    def add_field_entries(self, params):
        if self.fields_entries:
            params[str(self) + ".fields"] = ",".join(sorted(self._get_fields()))

    def _get_fields(self):
        return [a.field for a in self.fields_entries]

    def __str__(self):
        return self.resource_name


class FieldSelector(object):
    def __init__(self, field_name):
        self.field = field_name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.field.__eq__(other.field)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.field.__hash__()


class SimpleExpression(object):
    def __init__(self, property_name, value, op):
        self.property_name = property_name
        self.value = value
        self.op = op

    def apply_expression(self, query_string):
        query_string[self.property_name] = str(self.value)


class StringExpressionFactory(object):
    def __init__(self, property_name):
        self.property_name = property_name

    def equal_to(self, value):
        return SimpleExpression(self.property_name, value, Operator.EQUALS)

    @classmethod
    def field(cls, property_name):
        return StringExpressionFactory(cls.build_with(property_name))

    @classmethod
    def build_with(cls, property_name):
        return "with" + property_name[0].upper() + property_name[1:]


class Operator(enum.Enum):
    EQUALS = 1
    LIKE = 2
