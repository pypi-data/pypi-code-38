def entity(table_name, version, primary_key, fields):
    def decorator(fn):
        def decorated(*args, **kwargs):
            return fn(*args, **kwargs)

        decorated._table_name = table_name
        decorated._version = version
        decorated._primary_key = primary_key
        decorated._fields = fields

        return decorated
    return decorator



