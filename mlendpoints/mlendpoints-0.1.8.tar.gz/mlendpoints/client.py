from .communication import send_requests, receive_requests


def Model(name, info_address, query_address=None):
    res = send_requests('get_info', {'name': name}, {}, info_address)
    jsdata, _ = receive_requests(res)
    if query_address is not None:
        jsdata['address'] = query_address

    # construct a class from the metadata in info
    m = decode_class(jsdata)
    return m


def decode_class(info):
    m = type(info['name'], (), {})
    for method in info['methods']:
        setattr(m, method['name'],
                create_function(method['args'], method['defaults'],
                                method['name'], info['address']))
    return m


def create_function(desired_args, defaults, name, address):
    def standard_func(*args, **kwargs):
        if len(args) > len(desired_args):
            desstr = "1 positional argument" if len(desired_args) == 1 else "{} positional arguments".format(len(desired_args))
            givstr = "1 was" if len(args) == 1 else "{} were".format(len(args))
            msg = "{}() takes {} but {} given".format(name, desstr, givstr)
            raise TypeError(msg)
        inp = {}
        for key in kwargs:
            if key not in desired_args:
                raise TypeError("{}() got unexpected keyword argument '{}'"
                                .format(name, key))
            inp[key] = kwargs[key]
        for i, arg in enumerate(args):
            key = desired_args[i]
            if key in inp:
                raise TypeError("{}() got multiple values for argument '{}'"
                                .format(name, key))
            inp[key] = arg
        for i, arg in enumerate(reversed(defaults)):
            key = desired_args[-(i + 1)]
            if key not in inp:
                inp[key] = arg
        for arg in desired_args:
            if arg not in inp:
                raise TypeError(
                    "{}() missing required positional argument '{}'"
                    .format(name, arg))
        res = send_requests("get_method", {"method": name}, inp, address)
        jsdata, argdata = receive_requests(res)
        return argdata
    return staticmethod(standard_func)
