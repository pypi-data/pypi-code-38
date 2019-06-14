# -*- coding: utf-8 -*-
import platform, string, json, re, hashlib
from os import mkdir
from os.path import join, exists, sep, abspath, dirname

from jinja2 import Environment, FileSystemLoader

from api_generator.helpers.log import log
from argus_cli.helpers.formatting import from_safe_name, to_safe_name


JINJA_ENGINE = Environment(loader=FileSystemLoader(abspath(join(dirname(__file__), "..", "templates"))))

# Declare filters for converting arguments to safe argument names if they're
# built-in keywords
JINJA_ENGINE.filters['to_safe_argument'] = to_safe_name
JINJA_ENGINE.filters['from_safe_argument'] = from_safe_name
JINJA_ENGINE.filters['safe_dict_dump'] = lambda d: json.dumps(d, sort_keys=True)


def write_endpoints_to_disk(endpoints, output, api_url, with_plugin_decorators=False) -> None:
    """Outputs the directory structure with all endpoints

    :param list endpoints: List of endpoints generated with build_endpoint_structure
    """
    log.debug("Generating static API files to %s" % output)

    def find(key, dictionary):
        """Finds all occurances of a key in nested list
        """
        for k, v in dictionary.items():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in find(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find(key, d):
                        yield result

    endpoints = [endpoint for endpoint in find("__METADATA__", endpoints) if isinstance(endpoint, dict)]

    def create_python_module(path):
        if not exists(join(*path)):
            mkdir(join(*path))
        if not exists(join(*(path + ["__init__.py"]))):
            with open(join(*(path + ["__init__.py"])), "w") as init:
                init.write(
                    JINJA_ENGINE.get_template("init.j2").render()
                )

    for endpoint in sorted(endpoints, key=lambda endpoint: "-".join(endpoint["__PATH__"])):
        path = output.split(sep)
        if platform.system() == "Windows" and re.match(r"^[A-Z]:", path[0]):
            # Add a seperator if there is just a drive without a seperator.
            # Without the sepeartor it's a relative directory
            path[0] += sep
        elif platform.system() != "Windows":
            # Add root (/) separator
            path.insert(0, sep)

        # Create directory tree
        if not exists(join(*path)):
            mkdir(join(*path))
        with open(join(*(path + ["__init__.py"])), "wb") as init:
            from time import time
            init.write(
                JINJA_ENGINE.get_template("init.j2")
                    .render(created_at=time(), api_url=api_url)
                    .encode("utf8")
            )

        for directory in endpoint["__PATH__"]:
            path.append(directory)

            # Write file
            if directory == endpoint["__PATH__"][-1]:
                filename = endpoint["__MODULE_NAME__"] or "__init__"
                if not endpoint["__MODULE_NAME__"] and endpoint["__PATH__"][-1] == '':
                    endpoint["__PATH__"] .pop()

                endpoint_file_path = join(*(path[:-1] + ["%s.py" % filename]))

                with open(endpoint_file_path, "rb+" if exists(endpoint_file_path) else "wb+") as endpoint_file:
                    method_names = []
                    endpoint_request_methods = []

                    # Never print the same method twice
                    for method in sorted(endpoint["__REQUEST_METHODS__"], key=lambda method: method.name):
                        if method.name not in method_names:
                            endpoint_request_methods.append(method)
                        method_names.append(method.name)

                    # Write endpoint templates to file, and decorate them
                    # with the plugin command registration decorator if with_plugin_decorators=True
                    try:
                        contents = endpoint_file.read().decode('utf-8')
                        expected_contents = JINJA_ENGINE.get_template("endpoint.j2").render(
                            endpoint=endpoint_request_methods,
                            path=endpoint["__PATH__"],
                            register_as_plugin=with_plugin_decorators
                        )

                        if hashlib.md5(contents.encode("utf-8")).hexdigest() != hashlib.md5(expected_contents.encode("utf-8")).hexdigest():
                            log.debug("Generating endpoint: %s" % "/".join(endpoint["__PATH__"]))
                            endpoint_file.seek(0)
                            endpoint_file.write(
                                expected_contents.encode("utf-8")
                            )
                            endpoint_file.truncate()

                            log.debug("Generating test helpers for endpoint: %s" % "/".join(endpoint["__PATH__"][:-1]))

                            # Create a directory for test decorators
                            create_python_module(path[:-1] + ["test_helpers"])
                            create_python_module(path[:-1] + ["test_helpers", endpoint["__MODULE_NAME__"]])
                            for request_method in endpoint["__REQUEST_METHODS__"]:
                                test_helper_path = path[:-1] + ["test_helpers", endpoint["__MODULE_NAME__"], "%s.py" % request_method.name]
                                # create_python_module(test_helper_path)
                                with open(join(*test_helper_path), "wb+") as test_helper:
                                    try:
                                        test_helper.write(
                                            JINJA_ENGINE
                                                .get_template("test_helpers/request.mock.j2")
                                                .render(method=request_method)
                                                .encode("utf-8")
                                        )
                                    except Exception as error:
                                        log.error(error)
                        else:
                            log.debug("Up to date: %s" % "/".join(endpoint["__PATH__"]))
                    # Catch all exceptions because it could come from Jinja, File, or
                    # elsewhere, and no matter what exception it is, we want to log it
                    # instead of failing silently as it would otherwise
                    except Exception as error:
                        log.error(error)
            else:
                # Create directory tree
                create_python_module(path)
