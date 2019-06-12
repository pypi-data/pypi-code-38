import time


class EventSnapshot(object):
    def __init__(self):
        self.ts = int(round(time.time() * 1000))
        self.stack_trace = []

    def add_frame(self, _frame):
        self.stack_trace.append(_frame)

    def as_dict(self):
        return {
            'ts': self.ts,
            'stacktrace': [st.as_dict() for st in self.stack_trace]
        }

    def add_frames(self, fr):
        self.stack_trace = self.stack_trace + fr

    def set_frames(self, fr):
        self.stack_trace = fr


class Watcher(object):
    def __init__(self, name, expression):
        self.values = []
        self.name = name
        self.expression = expression

    def add_variable(self, watcher):
        self.values.append(watcher)

    def as_dict(self):
        return {
            'name': str(self.name),
            'expression': self.expression,
            'variables': [wat.as_dict() for wat in self.values]
        }


class SnapshotFrame(object):
    def __init__(self, class_name, method_name, line_number, file_name, depth):
        self.class_name = class_name
        self.method_name = method_name
        self.line_number = line_number
        self.file_name = file_name
        self.depth = depth
        self.variables = []

    def add_variable(self, f_variable):
        self.variables.append(f_variable)

    def set_variables(self, variables):
        self.variables = variables

    def as_dict(self):
        return {
            'classname': self.class_name,
            'filename': self.file_name,
            'methodname': self.method_name,
            'linenumber': self.line_number,
            'depth': self.depth,
            'variables': [_variable.as_dict() for _variable in self.variables]
        }


class VariableId(object):
    def __init__(self, v_id, v_name):
        self.id = v_id
        self.name = v_name

    def as_dict(self):
        return {
            'id': self.id,
            'name': str(self.name)
        }


class Variable(VariableId):
    def __init__(self, name, v_id, v_type, value, v_hash):
        # python 2.7 needs the class and self to be passed to super
        super(Variable, self).__init__(v_id, name)
        self.type = v_type
        self.value = value
        self.hash = v_hash
        self.fields = []

    def add_variable(self, field):
        self.fields.append(field)

    def as_dict(self):
        return {
            'id': self.id,
            'name': str(self.name),
            'type': self.type.__name__,
            'value': self.value,
            'hash': self.hash,
            'children': [field.as_dict() for field in self.fields]
        }

