import inflection
import os
import functools

class Router(object):
    paths = ["/"]
    def __init__(self,app, controller):
        self.controller = controller
        self.app = app

    def __enter__(self):
        self.controller().routes(self.app, base=os.path.join(*Router.paths))
        Router.paths.append(self.controller.get_root())
        Router.paths.append(self.controller.get_id())

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

    class NoRouteExists(BaseException):
        pass

    class Controller(object):
        def __init__(self):
            cls = self.__class__
            self._root = cls.get_root()
            self._resource = cls.get_resource()
            self._id  = cls.get_id()

            self.options = dict()

        @classmethod
        def get_root(cls):
            return inflection.underscore(cls.__name__.replace("App", ""))

        @classmethod
        def get_resource(cls):
            return inflection.singularize(cls.get_root())

        @classmethod
        def get_id(cls):
            return "<{resource}_id>".format(resource=cls.get_resource())

        def create(self):
            raise Router.NoRouteExists("No such route is defined")

        def index(self):
            raise Router.NoRouteExists("No such route is defined")

        def update(self):
            raise Router.NoRouteExists("No such route is defined")

        def delete(self):
            raise Router.NoRouteExists("No such route is defined")

        def show(self):
            raise Router.NoRouteExists("No such route is defined")

        def routes(self, app, base="/"):
            cls = self.__class__
            list_route = os.path.join(base, self._root)
            item_route = os.path.join(base, self._root, self._id)

            obj = self

            for attr in dir(self):
                if attr in dir(Router.Controller): #['route','routes','index','create','show','update','delete']:
                    continue
                if attr[0] == "_":
                    continue

                method = getattr(self, attr)
                if callable(method):
                    custom_route = os.path.join(list_route,attr)
                    qualname = "{klass}.{method}".format(klass=cls.__name__,method=attr)
                    options = Router.route.options.get(qualname,{})

                    app.add_url_rule(
                        custom_route,
                        qualname,
                        attr,
                        **options)

            app.add_url_rule(list_route, "{klass}.index".format(klass=cls.__name__),obj.index,methods=["GET"])
            app.add_url_rule(list_route, "{klass}.create".format(klass=cls.__name__),obj.create,methods=["POST"])
            app.add_url_rule(item_route, "{klass}.show".format(klass=cls.__name__), obj.show, methods=["GET"])
            app.add_url_rule(item_route, "{klass}.update".format(klass=cls.__name__), obj.update, methods=["PUT","PATCH"])
            app.add_url_rule(item_route, "{klass}.delete".format(klass=cls.__name__), obj.delete, methods=["DELETE"])


"""
Example: 
class AppTestplans(Router.Controller):
    def update(self, id):
        return "AppTestplans::update"

    @Router.route(methods=["POST"])
    def custom(self, id):
        return "AppTestplans::custom"



class AppTestcases(Router.Controller):
    pass

"""






