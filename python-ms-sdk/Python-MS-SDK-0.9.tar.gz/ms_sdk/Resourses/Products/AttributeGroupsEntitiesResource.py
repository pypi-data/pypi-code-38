from ms_sdk.Resourses.Resource import Resource


class AttributeGroupsEntitiesResource(Resource):
    """
    Class AttributeGroupsEntitiesResource
    :method AttributeGroupsEntities get(int id):
    :method AttributeGroupsEntities first():
    :method AttributeGroupsEntities[] all():
    :method AttributeGroupsEntities update(id, data):
    :method AttributeGroupsEntities create(data):
    """

    def getURI(self):
        return 'attributegroupsentities'
