from ms_sdk.Resourses import Resource


class MessagesResource(Resource):
    """
    Class MessagesResource
    :method Message get(int id):
    :method Message first():
    :method Message[] all():
    :method Message update(id, data):
    :method Message create(data):
    """

    def getURI(self):
        return 'messages'