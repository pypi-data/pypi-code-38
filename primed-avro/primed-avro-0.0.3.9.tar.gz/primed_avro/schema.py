import json


class SchemaMeta:
    def __init__(self, subject, version, id, schema):
        self.subject = subject
        self.version = version
        self.id = id
        if isinstance(schema, str):
            self.schema = json.loads(schema)
        elif isinstance(schema, dict):
            self.schema = schema
        else:
            raise Exception(
                "Unsupported schema type, expected `str` or `dict` but was {}".format(
                    type(schema)
                )
            )


class Schema:
    def __init__(self, schema, id):
        self.id = id
        self.schema = json.loads(schema)
