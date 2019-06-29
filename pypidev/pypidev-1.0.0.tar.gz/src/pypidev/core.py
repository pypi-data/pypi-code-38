""" Core pypidev """

class Hello(object):

    def __init__(self, name):
        self.name = name

    def get(self):
        return "Hello, {}!".format(self.name)
