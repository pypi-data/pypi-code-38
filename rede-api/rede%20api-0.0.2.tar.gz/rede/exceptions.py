# coding: utf-8

class GetAuthorizedException(Exception):
    def __init__(self, id, message=None):
        self.id = id
        self.message = message

    def __str__(self):
        return u'%s - %s' % (self.id, self.message)


class RequestGetError(Exception):
    def __init__(self, statuscode, message=None):
        self.statuscode = statuscode
        self.message = message 

    def __str__(self):
        return u'%s - %s' % (self.statuscode, self.message)