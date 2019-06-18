from ms_sdk.Resourses.Resource import Resource


class MediaResource(Resource):
    """
    Class MediaResource
    :method Media get(int $id):
    :method Media first():
    :method Media[] all():
    :method Media update($id, $data):
    :method Media create($data):
    """

    def getURI(self):
        return 'images'
