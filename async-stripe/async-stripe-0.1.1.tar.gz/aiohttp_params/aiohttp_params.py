def session_complex_params(session):
    session.post = patch_params(session.post)
    session.get = patch_params(session.get)
    session.put = patch_params(session.put)
    return session

def patch_params(request_method):

    def decorated_request(*args, **kwargs):
        try:
            kwargs["params"] = format_params(kwargs["params"])
        except KeyError:
            pass
        return request_method(*args, **kwargs)

    return decorated_request


def format_params(params):
    return '&'.join(format_param(*item) for item in params.items())


def format_param(k, v):
    if isinstance(v, list):
        return format_list_param(k, v)
    if isinstance(v, dict):
        return format_dict_param(k, v)
    return format_simple_param(k, v)


def format_dict_param(key, dic):
    return '&'.join(f"{key}[{k}]={str(v)}" for k, v in dic.items())


def format_list_param(key, li):
    li = map(str, li)
    return f"{key}[]={','.join(li)}"


def format_simple_param(key, value):
    return f"{key}={value}"
