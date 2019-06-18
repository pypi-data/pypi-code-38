from ms_sdk.Resourses import Resource


class UserEventsResource(Resource):
    """
    Class MessagesResource
    :method Message get(int id):
    :method Message first():
    :method Message[] all():
    :method Message update(id, data):
    :method Message create(data):
    """

    def getURI(self):
        return 'userevents'