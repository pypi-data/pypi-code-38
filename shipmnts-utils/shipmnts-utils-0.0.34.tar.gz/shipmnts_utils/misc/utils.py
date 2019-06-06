from rest_framework.renderers import JSONRenderer


def standardize_response(response):
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    return response
