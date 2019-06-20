# -*- coding: utf-8 -*-

def get_exception_description(e):
    return u"%s: %s" % (e.__class__.__name__, e)

class EmptyContentError(Exception):
    pass

class LogginRequired(Exception):
    pass
