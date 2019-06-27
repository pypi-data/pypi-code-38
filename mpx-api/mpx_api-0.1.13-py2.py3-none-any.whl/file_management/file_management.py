from mpxapi.api_base import ApiBase
import json

class FileManagement(ApiBase):
    def __init__(self, api):
        ApiBase.__init__(self, api)

        self.schema = "1.6"
        self.service = "File Management Service"
        self.path = "/web/FileManagement"

    def link_new_file(self, data, params=None):
        if not params:
            params = {}

        return self.api.command(service=self.service, path=self.path, method="POST",
                            params=self.apply_schema(params),
                            data=json.dumps({'linkNewFile': data}))
