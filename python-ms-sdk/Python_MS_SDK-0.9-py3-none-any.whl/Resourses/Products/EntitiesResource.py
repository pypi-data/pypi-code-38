from ms_sdk.Resourses.Resource import Resource


class EntitiesResource(Resource):
    """
    Class EntitiesResource
    :method SMEntity get(int id):
    :method SMEntity first():
    :method SMEntity[] all():
    :method SMEntity update(id, data):
    :method SMEntity create(data):
    """

    def getURI(self):
        return 'entities'
