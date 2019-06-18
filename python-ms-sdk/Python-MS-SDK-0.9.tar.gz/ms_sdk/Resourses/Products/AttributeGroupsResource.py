from ms_sdk.Resourses.Resource import Resource


class AttributeGroupsResource(Resource):
    """
    Class AttributeGroupsResource
    :method AttributeGroup get(int id):
    :method AttributeGroup first():
    :method AttributeGroup[] all():
    :method AttributeGroup update(id, data):
    :method AttributeGroup create(data):
    """

    def getURI(self):
        return 'attributegroups'
