from ms_sdk.Resourses.Resource import Resource


class MediaTypesResource(Resource):
    """
    Class MediaTypeResource
    :method MediaType get(int $id):
    :method MediaType first():
    :method MediaType[] all():
    :method MediaType update($id, $data):
    :method MediaType create($data):
    """

    def getURI(self):
        return 'imagetypes'
