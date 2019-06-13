
import os
import configparser

class Config(object):
    def __init__(self, filename=None):
        if not filename:
            filename = os.path.expanduser('~/.config/odoopti.cfg')
        self._conf = configparser.ConfigParser()
        self._conf.read([filename])

    def get(self, section, name):
        return self._conf.get(section, name)

    def getint(self, section, name):
        return self._conf.getint(section, name)

    def env_get(self, env, name):
        return self.get('env:{}'.format(env), name)

    def env_getint(self, env, name):
        return self.getint('env:{}'.format(env), name)
