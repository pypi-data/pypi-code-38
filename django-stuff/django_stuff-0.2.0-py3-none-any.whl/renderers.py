import json

from rest_framework import renderers
from rest_framework.utils import encoders

import openapi_codec
import coreapi


class SwaggerRenderer(renderers.BaseRenderer):
    media_type = 'application/openapi+json'
    format = 'swagger'

    def render(self, data, media_type=None, renderer_context=None):

        if isinstance(data, coreapi.Document):
            codec = openapi_codec.OpenAPICodec()
            return codec.dump(data)

        return json.dumps(
            data,
            cls=encoders.JSONEncoder,
            indent=4
        )
