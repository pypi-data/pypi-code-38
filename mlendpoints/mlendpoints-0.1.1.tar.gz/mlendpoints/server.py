from tornado import web, ioloop
import os
import inspect
import simplejson


class MainHandler(web.RequestHandler):
    def initialize(self, model, info):
        self.model = model
        self.info = info
        self.methods = set([m['name'] for m in self.info['methods']])

    def post(self):
        req = simplejson.loads(self.request.body)
        if req['cmd'] == 'get_info':
            if req['name'] == self.info['name']:
                self.write(self.info)
            else:
                print('name "{}" requested which is not "{}"'
                      .format(req['name'], self.info['name']))
        if req['cmd'] == 'get_method':
            if req['method'] in self.methods:
                res = getattr(self.model, req['method'])(**req['kwargs'])
                self.write(simplejson.dumps({'data': res}))


class Server(object):
    def __init__(self, model):
        self.model = model
        self.info = get_doc_info(self.model)

    def show(self, debug=True):
        loop = ioloop.IOLoop.instance()
        app = web.Application([
                (r"/", MainHandler, {'model': self.model, 'info': self.info})],
                 debug=debug)
        app.listen(self.info['port'])
        print('serving model with name "{}" at {}'
              .format(self.info['name'], self.info['address']))
        loop.start()


def get_doc_info(m):
    """Returns a json representation of the class and its staticmethods
       name:
       doc:
       port:
       address:
       methods: [
           {name: , doc: , args: [], defaults: []}
       ]
    """
    info = {}
    info['name'] = type(m).__name__
    info['doc'] = m.__doc__.strip() if m.__doc__ is not None else ''
    info['methods'] = []
    for k in m.__class__.__dict__:
        v = m.__class__.__dict__[k]
        if isinstance(v, staticmethod):
            s = inspect.getargspec(getattr(m, k))
            row = {}
            row['name'] = k
            row['args'] = s.args
            defaults = [d for d in s.defaults] if s.defaults is not None\
                else []
            # check that defaults are jsonable
            try:
                simplejson.dumps(defaults)
            except Exception as e:
                print(e)
                raise TypeError(
                    "default values {} for method {}.{}() are not jsonable"
                    .format(defaults, info['name'], row['name']))
            row['defaults'] = defaults
            row['doc'] = getattr(m, k).__doc__.strip()\
                if getattr(m, k).__doc__ is not None else ''
            info['methods'].append(row)
    info['port'] = os.getenv('PORT', 5555)
    info['address'] = 'http://localhost:{}'.format(info['port'])
    return info
