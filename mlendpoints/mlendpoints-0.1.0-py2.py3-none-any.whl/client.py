import requests
import simplejson


def get_model(name, address):
    try:
        out = requests.post(address, json={'cmd': 'get_info',
                                           'name': name})
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError(
            "failed to connect to {}".format(address))
    info = simplejson.loads(out.content)

    # construct a class from the metadata in info
    m = decode_class(info)
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
        res = requests.post(address,
                            json={'cmd': 'get_method',
                                  'method': name, 'kwargs': inp})
        res = simplejson.loads(res.content)
        return res['data']
    return staticmethod(standard_func)
