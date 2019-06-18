from ms_sdk.Resourses import Resource


class TriggerResource(Resource):
    """
    Class TriggerResource
    :method Trigger create(data):
    """

    def getURI(self):
        return 'marketing/trigger'

    def limit(self, **kwargs):
        raise NotImplementedError

    def getLimit(self):
        raise NotImplementedError

    def delete(self, **kwargs):
        raise NotImplementedError

    def all(self):
        raise NotImplementedError

    def get(self, **kwargs):
        raise NotImplementedError