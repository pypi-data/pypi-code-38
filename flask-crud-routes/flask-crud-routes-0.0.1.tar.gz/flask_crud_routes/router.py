import flask
import inflection
import os
import contextlib
import functools

class Router():
    paths = ["/"]
    def __init__(self,app, controller):
        self.controller = controller
        self.app = app

    def __enter__(self):
        resource = inflection.underscore(self.controller.__name__.replace("App", ""))
        print(Router.paths)
        self.controller().routes(self.app, base=os.path.join(*Router.paths))
        Router.paths.append(resource)
        Router.paths.append("<{resource}_id>".format(resource=resource))


    def __exit__(self, exc_type, exc_val, exc_tb):
        Router.paths.pop()
        Router.paths.pop()

    class route:
        options = dict()

        def __init__(self, **options):
            self.options = options

        def __call__(self, fn):
            Router.route.options[fn.__qualname__] = self.options

            @functools.wraps(fn)
            def decorated(*args, **kwargs):
                fn(*args, **kwargs)

            return decorated


    class Controller(object):
        def __init__(self):
            self._root = inflection.underscore(self.__class__.__name__.replace("App", ""))
            self.options = dict()

        def create(self):
            return "CafyApp::create"

        def index(self):
            return "CafyApp::index"

        def update(self, id):
            return "CafyApp::update"

        def delete(self, id):
            return "CafyApp::delete"

        def show(self, id):
            return "CafyApp::show"

        @classmethod
        def route(self, **options):
            def decorator(f):
                self.options[f.__name__] = options

        #@contextlib.contextmanager
        def routes(self, app, base="/"):
            cls = self.__class__
            list_route = os.path.join(base, self._root)
            item_route = os.path.join(base, self._root,"<id>")

            print(cls.__name__)
            print(list_route)
            print(item_route)
            obj = self

            for attr in dir(self):
                if attr in ['route','routes','index','create','show','update','delete']:
                    continue
                if attr[0] == "_":
                    continue

                method = getattr(self, attr)
                if callable(method):
                    #import ipdb;
                    #ipdb.set_trace()
                    custom_route = os.path.join(list_route,attr)
                    print(self.options)
                    qualname = "{klass}.{method}".format(klass=cls.__name__,method=attr)
                    options = Router.route.options.get(qualname)
                    if options:
                        methods = options.get("methods",["GET"])

                    print(method)
                    print(Router.route.options)
                    #import ipdb;
                    #ipdb.set_trace()

                    app.add_url_rule(
                        custom_route,
                        qualname,
                        attr,
                        **options)

            app.add_url_rule(list_route,"{klass}.index".format(klass=cls.__name__),obj.index,methods=["GET"])
            app.add_url_rule(list_route,"{klass}.create".format(klass=cls.__name__),obj.create,methods=["POST"])
            app.add_url_rule(item_route, "{klass}.show".format(klass=cls.__name__), obj.show, methods=["GET"])
            app.add_url_rule(item_route, "{klass}.update".format(klass=cls.__name__), obj.update, methods=["PUT","PATCH"])
            app.add_url_rule(item_route, "{klass}.delete".format(klass=cls.__name__), obj.delete, methods=["DELETE"])


            #app.route(newroute, )(obj.create)
            #app.route(newroute, methods=["GET"])(obj.index)
            #app.route(item_route, methods=["GET"])(obj.show)
            #app.route(item_route, methods=["PUT","PATCH"])(obj.update)
            #app.route(item_route, methods=["DELETE"])(obj.delete)




class AppTestplans(Router.Controller):
    def update(self, id):
        return "AppTestplans::update"

    @Router.route(methods=["POST"])
    def custom(self, id):
        return "AppTestplans::custom"



class AppTestcases(Router.Controller):
    pass






