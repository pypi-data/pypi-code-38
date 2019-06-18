from ms_sdk.Resourses.Resource import Resource


class AttributeDisplayTypesResource(Resource):
    """
    Class AttributeDisplayTypesResource
    :method AttributeDisplayType get(int id):
    :method AttributeDisplayType first():
    :method AttributeDisplayType[] all():
    :method AttributeDisplayType update(id, data):
    :method AttributeDisplayType create(data):
    """

    def getURI(self):
        return 'attributedisplaytypes'
