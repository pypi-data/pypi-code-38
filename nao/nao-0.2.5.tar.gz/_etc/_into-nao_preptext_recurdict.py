# -*- coding: utf-8 -*-
"""
config

"""
from __future__ import division, print_function, unicode_literals

import os, sys, logging, logging.handlers, yaml, codecs, re, cherrypy

from docutils.core import publish_parts

from future.utils import iteritems

################################
# MISC HELPER FUNCTION

def path(*plus):
    # print(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *plus))

root_path = path('..') # the repository root from which diofa could be imported

# MISC HELPER FUNCTION
################################



################################
# CONFIG SETUP


class RecursiveDictionary(dict):
    """RecursiveDictionary provides the methods rec_update and iter_rec_update
    that can be used to update member dictionaries rather than overwriting
    them.

    Created 2009-05-20 by Jannis Andrija Schnitzer (jannis@itisme.org)
    https://gist.github.com/114831
    Modified 2012-12-01 by Szabolcs Blaga (szabolcs@syrus.hu)
    """
    def recurse(self, other, **third):
        """Recursively update the dictionary with the contents of other and
        third like dict.update() does - but don't overwrite sub-dictionaries.

        Example:
        >>> d = RecursiveDictionary({'foo': {'bar': 42}})
        >>> d.rec_update({'foo': {'baz': 36}})
        >>> d
        {'foo': {'baz': 36, 'bar': 42}}
        """
 
        self.iter_recurse(iteritems(other))
        self.iter_recurse(iteritems(third))

    def iter_recurse(self, iterator):
        for key, value in iterator:
            if key in self and isinstance(self[key], dict) and isinstance(value, dict):
                self[key] = RecursiveDictionary(self[key])
                self[key].recurse(value)
                self[key] = dict(self[key]) # avoid using multi-level recursive dictionaries
            else:
                self[key] = value

    def __repr__(self):
        return super(self.__class__, self).__repr__()


config = RecursiveDictionary()
for f in [path(n+'.yaml') for n in ('global', 'local')]:
    if os.path.isfile(f):
        c = yaml.safe_load(codecs.open(f, 'r', encoding='utf8'))
        if c is not None: config.recurse(c)

config = dict(config)

# CONFIG SETUP
################################


################################
# SET UP LOGGING

#log_path = path('..', 'temp', 'log')
#try: os.makedirs(log_path)
#except OSError: pass

DETAILS =   logging.Formatter('%(asctime)s - %(name)s %(levelname)s - %(message)s')
CONSOLE =   logging.Formatter('%(levelname)-8s - %(message)s')
# THREADS =   logging.Formatter('{levelname:1} {threadName:>10}: {message}', style='{') # Python 3
THREADS =   logging.Formatter('%(threadName)-10s %(name)-20s %(lineno)-4s %(asctime)s %(levelname)-7s %(message)s')
THREADS_A =   logging.Formatter('%(levelname)-7s %(threadName)-10s: %(message)s')
THREADS_B = logging.Formatter('<%(levelname)-7s %(threadName)-10s %(asctime)s - %(name)s>\n%(message)s')
FULL =      logging.Formatter('<%(levelname)-7s %(threadName)-10s %(asctime)s - %(name)s %(ip)-15s %(user)-4s>\n%(message)s')
#logging.basicConfig(format=console)
#logging.basicConfig(
#    level=logging.DEBUG,
#    format='%(levelname)-7s %(threadName)-10s %(asctime)s - %(name)s:\n\t%(message)s',
#)


class ConnInfo:
    """
    move to server, than no need to import cherrypy here
    """

    def __getitem__(self, name):
        """
        To allow this instance to look like a dict.
        """
        if name == "ip":
            try:
                result = cherrypy.request.remote.ip
            except:
                result = "<no:ip>"
        elif name == "user":
            try:
                result = cherrypy.user.id
            except:
                result = "<no:user>"
        else:
            result = self.__dict__.get(name, "?")
        return result

    def __iter__(self):
        """
        To allow iteration over keys, which will be merged into
        the LogRecord dict before formatting and output.
        """
        keys = ["ip", "user"]
        keys.extend(self.__dict__.keys())
        return keys.__iter__()


def logger(name):
    """returns the default logger for the modul"""
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    # log = logging.LoggerAdapter(log, ConnInfo())

    #~ TODO: log.addHandler(x)
    #~ log.addHandler(x)

    return log

# diofa default handler
# replace stdout to avoid conflict with citparser
_mdh = logging.StreamHandler(sys.stderr) # sys.stdout used to work perfectly with Apache...

debug = config['server'].get('debug', True)
if debug:
    print('DEBUG mode, log at DEBUG level, DB will be regenerated')
    _mdh.setLevel(logging.DEBUG)
else:
    print('Normal mode, log at INFO level')
    _mdh.setLevel(logging.INFO)

_mdh.setFormatter(THREADS)


root_log = logger(__name__) # root logger for diofa (every diofa logger inherits these settings)
    # logger('') - the real root logger - is not used because it would duplicate with cherrypy logging
    # the real root could be used if you remove the cherrypy handlers
    # BgTaskManager uses root_log to add/remove thread specific handlers
root_log.addHandler(_mdh)




log = root_log # specific logger for this root module (the same as root_log)


# error_file = os.path.join(log_path, 'error.log')
# info_file = os.path.join(log_path, 'info.log')
# debug_file = os.path.join(log_path, 'debug.log')

# log = logging.getLogger()
# log.setLevel(logging.DEBUG)



# error = logging.FileHandler(error_file)
# error.setLevel(logging.ERROR)
# error.setFormatter(details)

# # info = logging.handlers.TimedRotatingFileHandler(info_file, when='d', interval=1)
# # info.setLevel(logging.INFO)
# # info.setFormatter(details)

# debug = logging.handlers.TimedRotatingFileHandler(debug_file, when='d', interval=1)
# debug.setLevel(logging.DEBUG)
# debug.setFormatter(details)

# std = logging.StreamHandler(sys.stdout)
# std.setLevel(logging.DEBUG)
# std.setFormatter(console)

# log.addHandler(error)
# # log.addHandler(info)
# log.addHandler(debug)
# log.addHandler(std)

#logger = logging.getLogger

# log = logger(__name__)
# log.debug('hőúőúóüü')

# SETUP LOGGING
################################



################################
# POST PROCESSING CONFIG
# with docutils, log is already available here

def prepare_text(dic):
    "Itt inkább valamiféle rst-féle parsolás kellene"
    def icon_replace(match):
        # log.debug("Found icon: {0}".format(match.group(0)))
#        for g in match.groups():
#            log.debug('Icon element {0}'.format(g))

        x = '<i class="{0}"></i>'.format(" ".join(['icon-'+g for g in match.group(1).split(' ') if g]))
        # log.debug(x)
        return x


    for k,v in iteritems(dic):
        if isinstance(v, dict):
            dic[k] = prepare_text(v)
        else:
            t = publish_parts(v,writer_name='html')['html_body']
            # log.debug("Searching for icon tags...")
            t = re.sub(
                '\{([^{}]*)\}',
                icon_replace,
                t
            )

            dic[k] = t

    return dic

text = prepare_text(config.get('text', {}))


# print(text)

# log.debug("The recursively merged configuration:\n{0}\n".format(yaml.dump(config, default_flow_style=False)))

# POST PROCESSING CONFIG
################################











