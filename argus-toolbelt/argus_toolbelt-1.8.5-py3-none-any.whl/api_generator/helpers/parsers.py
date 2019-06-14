"""Supporting methods and classes for parsing request methods from API schemas"""
import re, json
from collections import OrderedDict
from os.path import abspath, join, dirname

from jinja2 import Environment, FileSystemLoader

from api_generator.helpers import tests
from api_generator.helpers import http
from argus_cli.helpers.formatting import python_name_for, to_snake_case, to_safe_name, from_safe_name
from api_generator.helpers.log import log
from api_generator.helpers.generator import JINJA_ENGINE


class RequestMethod(object):
    """Container for a RequestMethod, accepts all building blocks for a request method
    parsed by any parser, and provides functionality for creating an actual python
    method as a string that can be printed to file, or load that string as an actual
    function that can be executed.

    When loaded as an executable function, this function will also have attributes
    that can be used in tests, such as @function.success(), @function.unauthorized(),
    which will intercept any calls made to the URL declared in this request method,
    and respond with a fake response.

    For example, to write a test for alarms.get_alarms, you might want to decorate
    your function with:

    @alarms.get_alarms.success()
    def my_method():
        # Receives a fake response, no call to the server will be created:
        response = alarms.get_alarms()

    This class is an ABC, meaning it should not be used in its raw form. Parsers
    should subclass RequestMethod, and are responsible for overloading _fake_response
    (to parse and generate the response object into a fake response), and for passing
    the correct arguments to initialization.

    For example, you might want to have different parsers, and therefore different ways
    of parsing request methods, e.g `class RABLRequestMethod(RequestMethod`,
    `Swagger2RequestMethod(RequestMethod)`, `class OpenAPI3RequestMethod(RequestMethod)`.
    """
    def __init__(
        self,
        url: str,
        name: str,
        method: str,
        description: str,
        parameters: dict,
        response: list = None,
        errors: list = None
    ):
        self.url = url
        self.name = to_snake_case(name)
        self.method = method.lower()
        self.description = description
        self.parameters = parameters
        self.api_key_header_name = "Argus-API-Key"
        self.response = OrderedDict({
            key["name"]: key
            for key in sorted(response, key=lambda k: k["name"] if k and "name" in k else "")
            if key and "name" in key
        }) if response else {}

        self.errors = OrderedDict({ k: v for k, v in sorted(errors.items()) })
        self.auth_data = {}

        # Ensure parameters are sorted so that parameters
        # with a default value come first in the list
        if self.parameters["all"]:

            # Sort again so that all parameters with a default value come
            self.parameters["all"] = sorted(
                self.parameters["all"],
                key=lambda parameter: "default" in parameter
            )

            # Sort so that all parameters that are not required come last:
            self.parameters["all"] = sorted(
                self.parameters["all"],
                key=lambda parameter: "required" not in parameter or parameter["required"] is not True
            )

            # Ensure arguments are unique by name:
            unique_parameters = []
            name_list = []
            for param in self.parameters["all"]:
                if param["name"] not in name_list:
                    unique_parameters.append(param)
                    name_list.append(param["name"])
                else:
                    log.warn("[%s] Parameter %s is not unique" % (self.name, param["name"]))

            self.parameters["all"] = unique_parameters




    def to_template(self, **kwargs) -> str:
        """Creates a function from the Request Method specification"""
        return JINJA_ENGINE.get_template("request.j2").render(method=self, **kwargs)

    @property
    def to_function(self) -> callable:
        """Wrapper around _as_function for retrieving a standalone function
        When this property is used, the function will be attached to the
        fake scope 'runtime_generated_api', rather than the scope of the
        given module.

        To attach this function on a class, or module, use .as_method_on(cls)
        """
        return self._as_function('runtime_generated_api')

    @property
    def url_regex(self) -> str:
        """Returns a regex for matching the URL including its parameters"""
        url = self.url

        for parameter in self.parameters["path"]:
            if parameter["type"] == 'int':
                url = url.replace("{%s}" % parameter["name"], "\d+")
            else:
                url = url.replace("{%s}" % parameter["name"], "[\w\d\-]+")

        return url

    def to_method_on(self, cls):
        """Attaches this as a function on a class / module"""
        setattr(cls, self.name, self._as_function(cls.__module__))
        return cls

    def fake_response(self) -> dict:
        """Returns a fake response for this method

        :raises AttributeError: When the _fake_response method has not been overloaded
        :returns: A dict with fake data
        """
        return self._fake_response_factory()(self.response)

    # PRIVATE
    def _fake_response_factory(self):
        """Guard method, this method must be overridden in subclasses"""
        raise AttributeError(
            "Subclasses must override `_fake_response_factory` and"
            "return a method to generate fake responses!"
        )

    def __str__(self):
        """Printable representation of this object"""
        return "<RequestMethod: url=%s method=%s parameters=%s>" % \
        (self.url, self.method, ",".join([p["name"] for p in self.parameters["all"]]))


    def _as_function(self, target_module: str = 'runtime_generated_api') -> callable:
        """Calls self.to_template to create the function string,
        then loads it into the scope to ensure the method is loaded

        :param target_module: What scope to assign function on, e.g cls.__module__
        :returns: Callable function
        """
        # Compile the method into the imaginary runtime_generated_api module
        fake_function = compile(
            self.to_template(),
            target_module,
            'exec'
        )

        # Evaluate it into fake_globals, where it'll be accessible
        fake_globals = {}
        eval(fake_function, {}, fake_globals)

        # Create a regex to match this URL, including its URL parameters
        # so that the decorators can intercept calls to this URL
        url_regex = self.url_regex
        function = fake_globals[self.name]

        # Successful response decorator
        function.success = tests.response(
            re.compile(url_regex),
            method=self.method,
            json=self.fake_response()
        )

        # Unauthorized 401 response decorator
        function.unauthoried = tests.response(
            re.compile(url_regex),
            method=self.method,
            status_code=401
        )

        # Access denied 403 response decorator
        function.access_denied = tests.response(
            re.compile(url_regex),
            method=self.method,
            status_code=403
        )

        # Not found 404 response decorator
        function.not_found = tests.response(
            re.compile(url_regex),
            method=self.method,
            status_code=404
        )

        return function
