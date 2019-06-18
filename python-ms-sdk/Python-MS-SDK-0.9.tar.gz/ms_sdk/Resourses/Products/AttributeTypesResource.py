from ms_sdk.Resourses.Resource import Resource


class AttributeTypesResource(Resource):
    """
    Class AttributeTypesResource
    AttributeType get(int id)
    AttributeType first()
    AttributeType[] all()
    AttributeType update(id, data)
    AttributeType create(data)
    """

    def getURI(self):
        return 'attributetypes'
