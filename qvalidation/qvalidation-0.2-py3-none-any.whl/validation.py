from types import FunctionType
from collections import namedtuple, defaultdict

Rule = namedtuple('Rule', ['field', 'label', 'rule', 'args', 'message'])


class Validation:

    def __init__(self, data={}):
        self._data = data
        self._result_data = {}
        self._rules = []
        self._errors = {}


    def set_data(self, data):
        self._data = data
        return self

    def set_rule(self, field, rule,  label=None, args=None, message=None):
        label = label if label else field
        self._rules.append(Rule(field=field, label=label,rule=rule, args=args, message=message))
        return self

    def is_valid(self, run=False):
        return not self.is_invalid(run)

    def is_invalid(self, run=False):
        return bool(self.errors(run))

    def data(self, run=False):
        if run:
            self.run()

        return self._result_data


    def errors(self, run=False):
        if run:
            self.run()
        return self._errors


    def run(self):
        """Execute validation and return if is valid
        """
        self._errors = {}
        self._result_data = self._data.copy()

        for r in self._rules:
            if type(r.rule) is str:
                self._run(fn=locals()[r.rule], rule=r)
            elif type(r.rule) is FunctionType:
                self._run(fn=r.rule, rule=r)
            elif type(r.rule) in [tuple, list]:
                self._run(fn=r.rule[0], rule=r)

        return self.is_valid()

    def _run(self, rule, fn, param=None):
        data = self._result_data
        message = rule.message
        value = data.get(rule.field, None)

        result = fn(field=rule.field, label=rule.label, data=data,
                    value=value, args=rule.args, message=message)
        if type(result) in [tuple, list]:
            is_valid = result[0] if len(result) > 0 else False
            message = (result[1] if len(result) > 1 else None)
            message = rule.message if rule.message else message
        else:
            is_valid = result

        self._result_data = data
        if not is_valid:
            d = defaultdict(str)
            d.update(data)
            d['value'] = value
            d['label'] = rule.label
            d['field'] = rule.field
            d['args'] = rule.args
            template = message.replace('{', '{0[').replace('}', ']}')
            self._errors[rule.field] = template.format(d)
