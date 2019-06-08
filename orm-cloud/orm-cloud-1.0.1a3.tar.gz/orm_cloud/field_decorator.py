

def field(column_name, primary_key=False):
    def decorator(fn):
        def decorated(*args, **kwargs):
            return fn(*args, **kwargs)
        return decorated
    return decorator



