from types import SimpleNamespace


# TODO: make 'isEmpty' generic like the other utils


def isEmpty(lenAble):
    if isinstance(lenAble, SimpleNamespace):
        return len(lenAble.__dict__) is 0
    else:
        return len(lenAble) is 0
