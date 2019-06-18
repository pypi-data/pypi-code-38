from ms_sdk.Resourses.Resource import Resource


class AttributeValuesResource(Resource):
    """
    Class AttributeValuesResource
    :method AttributeValue get(int $id):
    :method AttributeValue first():
    :method AttributeValue[] all():
    :method AttributeValue update($id, $data):
    :method AttributeValue create($data):
    """

    def getURI(self):
        return 'attributevalues'
