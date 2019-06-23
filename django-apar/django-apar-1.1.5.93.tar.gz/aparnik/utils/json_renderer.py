from rest_framework.renderers import JSONRenderer

class JSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # data = {
        #     "msg": "",
        #     "data": data,
        #     "success": True
        # }
        return super(JSONRenderer, self).render(data, accepted_media_type, renderer_context)