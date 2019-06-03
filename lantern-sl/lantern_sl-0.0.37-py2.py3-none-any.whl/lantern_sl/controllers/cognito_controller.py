import os
import json

class CognitoController(object):
    """ Allow us to easily fetch cognito parsed data 
    """

    def __init__(self, debug=False):
        self.debug = debug if debug else os.getenv("LOCAL_USER", False)

    def get(self, attribute_name, request, json_parse=False):
        """ retrieve a specific attribute_name from cognito headers
        
        Arguments:
            attribute_name {str} -- attribute name to be searched in the header
            request {flask.request} -- Active request, in http request.
        
        Keyword Arguments:
            json_parse {bool} -- force a json parse if active (default: {False})
        
        Raises:
            Exception -- generic exception, example: no request was provided
            ValueError -- Any Value error, example: attribute_name not found in header
        
        Returns:
            [str | json] -- if json_parse is False, it returns the scalar value, if it's activated we return the json object. 
        """

        if not request:
            raise Exception(
                "You have to specify a valid `request` parameter (inside a http request)")
        if self.debug:
            _local_header = {
                "authorizer": '{"claims": {"custom:fullName": "local_user", "cognito:username": "local_user", "email": "local_user@lantern.tech", "email_verified": true}}',
                "Authorization": "{}".format(os.getenv("LOCAL_TOKEN", ""))
            }
            header_value = _local_header.get(attribute_name, None)
        else:
            header_value = request.headers.get(attribute_name, None)
        if not header_value:
            raise ValueError("{} not found in headers".format(attribute_name))

        if not json_parse:
            return header_value
        else:
            header_value = header_value.replace("'", '"')
            header_value_json = json.loads(header_value)
            return header_value_json


    def get_default(self, name, request, header_attribute_name="authorizer", container_node="claims"):
        """ Return a value or json using de default mapping
        
        Arguments:
            name {str} -- attribute name to be searched in header
            request {flask.request} -- request in active HTTP request
        
        Keyword Arguments:
            header_attribute_name {str} -- header key containing cognito data (default: {"authorizer"})
            container_node {str} -- second level node, containing cognito data (default: {"claims"})

        Returns:
            [str] -- Value in `request.header_attribute_name.container_node.name`
        """

        header_value = self.get(
            attribute_name=header_attribute_name, request=request, json_parse=True)
        if container_node:
            header_node = header_value.get(container_node, None)
            if not header_node:
                raise ValueError("'{}' container_node not found in header (inside: {})".format(
                    container_node, header_attribute_name))
            requested_value = header_node.get(name, None)
            if not requested_value:
                raise ValueError(
                    "'{}' value empty/not found in {}.{}".format(name, header_attribute_name, container_node))
            return requested_value

        authorizer = request.headers.get(header_attribute_name, None)
        if not authorizer:
            raise Exception('''
             It was impossible to find cognito authorizer in heders, check your zappa_settings.json
             Example:
             "authorizer": {
                    "type": "COGNITO_USER_POOLS",
                    "provider_arns": [
                        "arn:aws:cognito-idp:us-west-2:XXXXXXXXXXX:userpool/us-west-2_XXXXXXXXX"
                    ]
                },
                "context_header_mappings": {
                    "authorizer" : "authorizer"
                }
            ''')
