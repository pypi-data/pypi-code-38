from re import match, split
from prance import BaseParser
import json, collections


from argus_cli.settings import settings
from api_generator.schema import get_schema
from api_generator.helpers.urls import remove_url_parameters, extract_url_parameters
from api_generator.helpers.parsers import RequestMethod
from argus_cli.helpers.formatting import python_name_for, to_snake_case

from .openapi2 import flatten, recursively_replace_types_with_pythonic_types


class RecursionParser(BaseParser):
    """The ResolvingParser extends BaseParser with resolving references."""
    recursion_limit = 2

    def __init__(self, url = None, spec_string = None, lazy = False, recursion_limit = 2, **kwargs):
        """
        See :py:class:`BaseParser`.
        Resolves JSON pointers/references (i.e. '$ref' keys) before validating the
        specs. The implication is that self.specfication is fully resolved, and
        does not contain any references.
        """
        BaseParser.__init__(
         self,
         url = url,
         spec_string = spec_string,
         lazy = lazy,
         **kwargs
        )
        self.recursion_limit = recursion_limit

    def _recursion_handler(self, *args, **kwargs):
        """When recursion fails, or goes too deep, this function will be returned,
        so we return an empty array to halt the parsing in its tracks
        """
        return []

    def _validate(self):
        # We have a problem with the BaseParser's validate function: the
        # jsonschema implementation underlying it does not accept relative
        # path references, but the Swagger specs allow them:
        # http://swagger.io/specification/#referenceObject
        # We therefore use our own resolver first, and validate later.
        from prance.util.resolver import RefResolver
        resolver = RefResolver(
            self.specification,
            self.url,
            recursion_limit_handler=self._recursion_handler,
            recursion_limit=self.recursion_limit
        )
        resolver.resolve_references()
        self.specification = resolver.specs

        # Skip validation, because our Swagger files are invalid and we don't
        # care about it.
        #BaseParser._validate(self)


class RecursiveRequestMethod(RequestMethod):

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
        ) -> 'RecursiveRequestMethod':
        """Creates request methods from their Swagger definitions

        :param str api_url: API base url
        :param str endpoint_url: URL to API endpoint
        :param str method: GET / POST / PUT / PATCH / DELETE
        :param dict definition: Method definition
        """
        error_responses = {
            status_code: error
            for status_code, error in definition["responses"].items()
            if match(r'\d+', status_code) and 399 < int(status_code)
        }

        successful_response = next((
            [
              dict(name=key, **recursively_replace_types_with_pythonic_types(value))
              for key, value in response["schema"]["properties"].items()
            ]
            for status_code, response in definition["responses"].items()
            if match(r'\d+', status_code) and 199 < int(status_code) < 300
            and "schema" in response
            and "properties" in response["schema"]
        ), None)

        url_parameters = sorted([
                recursively_replace_types_with_pythonic_types(parameter)
                for parameter in definition["parameters"]
                if parameter["in"] in ("path", "query", "url")
            ],
            key=lambda parameter: int(bool("default" in parameter and parameter["default"])),
            reverse=True
        )

        body_parameters = list(
            flatten([
                [
                  dict(name=key, **recursively_replace_types_with_pythonic_types(value))
                  for key, value in parameter["schema"]["properties"].items()
                ]
                for parameter in definition["parameters"]
                if parameter["in"] in ("body",)
                and "schema" in parameter
                and "properties" in parameter["schema"]
            ])
        )

        all_parameters = url_parameters + list(body_parameters)

        return RecursiveRequestMethod(
            url="".join([api_url, endpoint_url]).replace("//", "/").replace(":/", "://"),
            method=method,
            name=definition["operationId"] if "operationId" in definition else method,
            description=definition["summary"],
            errors=error_responses,
            parameters={
                "path": url_parameters or [],
                "body": body_parameters,
                "all": all_parameters
            },
            response=successful_response or None
        )


def load(location: str):
    parser = RecursionParser(location)

    schema = parser.specification
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
            RecursiveRequestMethod.from_swagger_definition(
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
