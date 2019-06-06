import sys
from hapiplotserver.app import app
from hapiplotserver.config import config


def gunicorn(app, **kwargs):

    import sys

    def action(host='127.0.0.1',port=kwargs['port'], workers=kwargs['workers']):
        
        from gunicorn.app.base import Application
        
        class FlaskApplication(Application):
            def init(self, parser, opts, args):
                return {
                    'bind': '{0}:{1}'.format(host, port),
                    'workers': workers
                }
            
            def load(self):
                return app
        FlaskApplication().run()

    # The following is needed because Gunicorn will see this script's
    # command line arguments and thrown and error. Does not make
    # sense, but needed.
    sys.argv = [sys.argv[0]]  # Remove CL arguments; keep filename.

    action()


def hapiplotserver(**kwargs):

    conf = config(**kwargs)
    application = app(conf)

    __version__ = "0.0.5b0"

    url = 'http://127.0.0.1:'+str(conf['port'])+"/"
    print(' * hapiplotserver version ' + __version__)
    print(' * Starting server for ' + url)
    print(' * Using Python %d.%d.%d' % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    print(' * See ' + url + ' for API description.')
    print(' * Cache directory: ' + conf['cachedir'])

    if conf['workers'] == 0:
        application.run(port=conf['port'], threaded=conf['threaded'])
    else:
        from sys import platform
        if platform == "darwin" and sys.version_info < (3, 6):
            raise Exception('On OS-X, Python 3.6+ is needed if workers > 0. (A bug in system URL libraries prevents some URL reads from working with gunicorn.)')
        gunicorn(application, port=conf['port'], workers=conf['workers'])


def gunicornx(**kwargs):
    """
    Alternative way to use Gunicorn 
    (instead of python hapiplotserver.py with --workers argument)

    Run using multiple threads with Gunicorn and -w, e.g.,
      gunicorn -w 4 -b 127.0.0.1:5000 'hapiplotserver:gunicornx()'

    Note that the command line options must be passed as keywords when
    gunicorn is used and only a subset of options are allowed, e.g.,
      gunicorn ... 'hapiplotserver:gunicornx(port=5000, cachedir="/tmp/hapi-data", loglevel="default")'

    This no longer works because imports are not resolved. Would need to
    do a manual import of app.py and lib.py, e.g.,
      sys.path.insert(0, os.path.join(__file__, "app.py"))
      sys.path.insert(0, os.path.join(__file__, "lib.py"))
    when execution from command line detected.
    """

    cachedir = kwargs['cachedir'] if 'cachedir' in kwargs else CACHEDIR
    usecache = kwargs['usecache'] if 'usecache' in kwargs else USECACHE
    loglevel = kwargs['loglevel'] if 'loglevel' in kwargs else LOGLEVEL
    # TODO: Look for invalid keywords and warn.

    opts = {'cachedir': cachedir, 'usecache': usecache, 'loglevel': loglevel}
    application = app()
    application = config(application, **kwargs)
    return application
