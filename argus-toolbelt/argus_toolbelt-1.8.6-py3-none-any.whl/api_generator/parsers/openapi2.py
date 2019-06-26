import collections
from re import match, split
from jsonschema import RefResolver

from argus_cli.settings import settings
from api_generator.schema import get_schema
from api_generator.helpers.urls import remove_url_parameters, extract_url_parameters
from api_generator.helpers.parsers import RequestMethod
from argus_cli.helpers.formatting import python_name_for, to_snake_case


def flatten(nested_list: list) -> list:
    """Generator that flattens lists inside a list"""
    for item in nested_list:
        if isinstance(item, collections.Iterable) and not isinstance(item, (str, bytes, dict)):
            yield from flatten(item)
        else:
            yield item


class Swagger2RequestMethod(RequestMethod):
    """Structure for a request method, allowing it to be passed to a template,
    create mocks for tests, or spit out defined functions
    """

    def _fake_response_factory(self) -> callable:
        """Provides the method to generate a fake response"""
        from api_generator.helpers.tests import fake_response
        return fake_response

    @staticmethod
    def from_swagger_definition(
            api_url: str,
            endpoint_url: str,
            method: str,
            definition: dict
        ) -> 'Swagger2RequestMethod':
        """Creates request methods from their Swagger definitions

        :param str api_url: API base url
        :param str endpoint_url: URL to API endpoint
        :param str method: GET / POST / PUT / PATCH / DELETE
        :param dict definition: Method definition
        """

        # Find out what errors can be raised and what the expected response would be
        error_responses = {
            status_code: error
            for status_code, error in definition["responses"].items()
            if match(r'\d+', status_code) and 399 < int(status_code)
        }

        # Find out what the successful response would normally look like (as a dict)
        successful_response = next((
            response \
            for status_code, response in definition["responses"].items() \
            if match(r'\d+', status_code) and 199 < int(status_code) < 300
        ), None)

        url_parameters = [
            {
                "name": parameter,
                "type": str,
                "required": True
            }
            for parameter in extract_url_parameters(endpoint_url)
        ]

        # Parameters should be sorted by whether or not they're required
        url_parameters = sorted(
            url_parameters,
            key=lambda parameter: int(bool("default" in parameter and parameter["default"])),
            reverse=True
        )

        # Parameters with default arguments should come last; and required parameters
        # with no default arguments must come first. Nested lists are flattened.
        parameters = [
            param
            for param in flatten(definition["parameters"])
            if "name" in param
        ]

        parameters = sorted(
            sorted(parameters,
                   key=lambda parameter: int(bool("default" in parameter and parameter["default"])),
                   reverse=True
            ),
            key=lambda parameter: int(bool("required" in parameter and parameter["required"])),
            reverse=True
        )

        # Description:
        description = definition["summary"]

        if "description" in definition:
            description += "\n%s" % definition["description"]

        # Cast default arguments to their type:
        for param in parameters:
            if "default" in param and param["default"] \
            and "type" in param and isinstance(param["type"], str):
                default_type = __builtins__[str(param["type"])]
                if callable(default_type):
                    param["default"] = default_type(param["default"])

        return Swagger2RequestMethod(
            url="".join([api_url, endpoint_url]).replace("//", "/").replace(":/", "://"),
            method=method,
            name=definition["operationId"] if "operationId" in definition else method,
            description=description,
            errors=error_responses,
            parameters={
                "path": url_parameters or {},
                "body": [
                    param
                    for param in parameters
                    if param["name"] not in [p["name"] for p in url_parameters]
            ],
                "all": parameters
            },
            response=successful_response or None
        )


def add_endpoints(cls, endpoints):
    """Adds endpoint functions to a class, and adds bridging classes in between

    :param class cls: Class to add functions/classes to
    :param dict endpoints: Endpoints to add
    """
    for name, content in endpoints.items():
        if isinstance(content, dict) and not name.startswith('__'):
            new_endpoint = type(name.capitalize(), (object,), {})
            setattr(cls, name.capitalize(), new_endpoint)
            add_endpoints(new_endpoint, content)
        else:
            if isinstance(content, RequestMethod):
                content.to_method_on(cls)
            else:
                setattr(cls, name, content)


def recursively_resolve_references(
        reference: 'RefResolver',
        value,
        recursion_limit: int = 10
    ):
    """Recursively iterates through the swagger schema and resolves JSON references

    :param RefResolver reference: A RefResolver object used to resolve references
    :param value: Any value it comes across - starting with the schema object root
    :return:
    """
    # If value is a dict, proceed to figure out how to return this dict
    if isinstance(value, dict):
        # If we found a schema nested like { "schema": { "$ref": ""}}
        # then set value to value["schema"] and continue to resolve it further down
        if "schema" in value and "$ref" in value["schema"]:
            resolved = reference.resolve(value["schema"]["$ref"])[1]
            if "properties" in resolved and isinstance(resolved["properties"], dict):
                value = [
                    dict(value, name=key)
                    for key, value in resolved["properties"].items()
                ]
            else:
                value = resolved




        # If it contains items, we flatten that too and resolve the reference
        if "items" in value and "$ref" in value["items"]:
            value["items"] = reference.resolve(value["items"]["$ref"])[1]
            if recursion_limit:
                value["items"] = recursively_resolve_references(
                    reference,
                    value["items"],
                    recursion_limit=recursion_limit - 1
                )

    # Check again if this is a dict after attempting to resolve
    if isinstance(value, dict):
        # If it just contains a reference, immediately resolve it
        if "$ref" in value:
            if recursion_limit:
                return recursively_resolve_references(
                    reference,
                    reference.resolve(value["$ref"])[1],
                    recursion_limit=recursion_limit - 1
                )
            else:
                return reference.resolve(value["$ref"])[1]


    # Check again if this is a dict as it may have been converted
    # to a list if it was a properties dict
    if isinstance(value, dict) and recursion_limit:
        return {
            key: recursively_resolve_references(reference, val, recursion_limit - 1)
            for key, val in value.items()
        }

    # Same goes for lists
    elif isinstance(value, list) and recursion_limit:
        return [
            recursively_resolve_references(reference, val, recursion_limit - 1)
            for val in value
        ]

    # Now we've hit a single base value, and can just return
    return value


def recursively_replace_types_with_pythonic_types(schema, recursion_limit: int = 100):
    """Recurses through a nested dict, looking for keys 'type', and 'format'.
    The "format" key will be removed as it's superfluous, and the "type" key will
    have its value replaced with the Python equivalent of that type.

    :param dict schema: Will be the root dictionary at the start
    :param int recursion_limit: Limits recursion to avoid maximum recursion depth
    """
    if isinstance(schema, dict):
        # If we ever hit a dict containing only "type" and "format", or only "type",
        # replace it with the python name for that type instead
        if (
            list(schema.keys()).sort() == ["format", "type"]
            or list(schema.keys()) == ["type"]) \
            and isinstance(schema["type"], str):
            schema = { "type": python_name_for(schema["type"]) }

        elif "type" in schema:
            if "type" in schema["type"]:
                if "enum" in schema["type"]:
                    schema.update({
                        "options": schema["type"]["enum"]
                    })
                schema.update({
                    "type": python_name_for(schema["type"]["type"])
                })
            else:
                schema.update({
                    "type": python_name_for(schema["type"])
                })

            if "format" in schema:
                del schema["format"]

        if recursion_limit:
            return {
                key: recursively_replace_types_with_pythonic_types(
                    value,
                    recursion_limit - 1
                ) \
                if isinstance(value, (dict, list)) else value
                for key, value in schema.items()
            }
    elif isinstance(schema, list) and recursion_limit:
        return [
            recursively_replace_types_with_pythonic_types(
                value,
                recursion_limit - 1
            )
            for value in schema
        ]

    return schema


def recursively_flatten_properties(schema, recursion_limit = 100):
    """Recursively flattens all 'properties' keys in the schema, to avoid
    unnecessary and unwanted nesting

    :param schema: Any value it comes across while recursing
    """
    if isinstance(schema, dict):
        schema = {
            key: (
                value["properties"]
                if isinstance(value, dict) and "properties" in value
                else value
            )
            for key, value in schema.items()
        }

    # Continue recursing if we're allowed
    if recursion_limit:
        if isinstance(schema, list):
             return [
                recursively_flatten_properties(value, recursion_limit - 1)
                for value in schema
            ]
        elif isinstance(schema, dict):
            return {
                key: recursively_flatten_properties(
                    value,
                    recursion_limit - 1
                )
                for key, value in schema.items()
            }

    return schema


def load(location: str) -> dict:
    """This is the main entry point of the OpenAPI2 parser. It loads the given
    OpenAPI 2.0 definition, and makes sure it's saved to disk, and that
    references are resolved, and javascript type names replaced with Python
    type names.

    It'll then begin setting up the nested endpoint structure, and create
    RequestMethods for each API endpoint before loading these as templates.

    The returned structure will be a nested dict representing the paths to each
    endpoint, where some dicts (the actual endpoints) will contain keys with
    metadata such as ["__METADATA__"]["__MODULE_NAME__"] and other useful
    data.

    It's up to the application to make use of these endpoints, e.g call
    nested_dict_structure_to_class_structure(endpoints), or whatever else
    you may want to do with these.

    If the endpoint structure has been loaded previously, the already loaded
    structure will be returned.
    """
    schema = get_schema(location)

    schema = recursively_resolve_references(RefResolver.from_schema(schema), schema)
    schema = recursively_flatten_properties(schema)
    schema = recursively_replace_types_with_pythonic_types(schema)
    api_url = settings["api"]["api_url"]

    # Contains all endpoints as a dict, to make lookup quick and easy
    endpoints = {}

    for endpoint, endpoint_definition in sorted(schema["paths"].items()):
        current_endpoint = endpoints

        # Set up "bridge classes" (The Components.V1 part of System.Components.V1)
        # Skip first url partsince the string will start with a slash
        url_parts = remove_url_parameters(endpoint).split('/')[1:]

        for index, part in enumerate(url_parts):
            last_part = url_parts[index - 2 if index - 2 >= 0 else 0]
            if len(last_part) >= 2 and last_part[0] == "v" and last_part[1:].isdigit():
                # We don't want to have anything deeper than 1 level after the version.
                # All endpoints under the namespaces after vX should
                # have unique names anyways.
                break
            if part == '':
                # The URL parameter removal will leave some blanks, so we ignore them
                continue
            elif part not in current_endpoint:
                current_endpoint[part] = {}
            current_endpoint = current_endpoint[part]

        url_parameters = [
            {
                "name": parameter,
                "type": str,
                "required": True
            }
            for parameter in extract_url_parameters(endpoint)
        ]

        if "__METADATA__" not in current_endpoint:
            # Join the ["url", "v1", "parts"] into a comma separated string of parts
            class_name = ",".join(url_parts)

            # Then remove ,v1, or ,v2, and take whatever comes after the version
            class_name = split(r',v\d+,', class_name)[1:]

            # Again split the remainder to get all the parts after the versioning
            class_name = "".join(class_name).split(",")

            # Join that back into one class name, with each word capitalized
            class_name = "".join(list(map(str.capitalize, class_name)))

            # Endpoint name will come out as AlarmsV1Alarm, while class name will
            # come out as Alarm
            endpoint_name = "".join(list(map(str.capitalize, url_parts)))

            current_endpoint["__METADATA__"] = {
                "__REQUEST_METHODS__": [],
                "__MODULE_NAME__": to_snake_case(class_name),
                "__ENDPOINT_NAME__": endpoint_name,
                "__CLASS_NAME__": class_name,
                "__PATH__": url_parts,
                "__IDENTIFIER__": "/".join(url_parts[:-1] + [class_name])
            }

        current_endpoint["__METADATA__"]["__REQUEST_METHODS__"] += [
            Swagger2RequestMethod.from_swagger_definition(
                api_url,
                endpoint,
                method,
                definition
            )
            for method, definition in endpoint_definition.items()
        ]

        for method in current_endpoint["__METADATA__"]["__REQUEST_METHODS__"]:
                current_endpoint[method.name] = method

    # Return a flattened list to be iterated and written to disk
    return endpoints
