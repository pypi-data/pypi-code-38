import re
import requests
from collections import OrderedDict

from requests.exceptions import HTTPError

from api_generator.helpers.log import log


def get_schema(location: str) -> dict:
    """Loads JSON schema from a file or URL

    :param location: Location of the swagger file. Can either be a URL or file URI
    :returns: Swagger JSON in a dict
    """
    if not re.match(r"^https?:\/\/", location):
        raise ValueError("The API schema location is not a valid URL or path on the filesystem: %s" % location)

    log.debug("Fetching swagger definition from %s" % location)
    response = requests.get(location)
    if not response.ok:
        raise HTTPError(
            "Error while retrieving swagger json from %s. (Status: %s)"
            % (location, response.status_code)
        )

    schema = response.json(object_pairs_hook=OrderedDict)

    return schema
