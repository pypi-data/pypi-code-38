from ms_sdk.Resourses.Resource import Resource


class ProductAttributeValuesResource(Resource):
    """
    Class ProductAttributeValuesResource
    :method Attribute get(int $id):
    :method Attribute first():
    :method Attribute[] all():
    :method Attribute update($id, $data):
    :method Attribute create($data):
    """

    def getURI(self):
        return 'productattributevalues'
