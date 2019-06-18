from ms_sdk.Resourses.Resource import Resource


class AttributesResource(Resource):
    """
    Class AttributesResource
    :method Attribute get(int id):
    :method Attribute first():
    :method Attribute[] all():
    :method Attribute update(id, data):
    :method Attribute create(data):
    """

    def getURI(self):
        return 'attributes'

    def belong(self, entityClass, attributeGroupId=None, attributeId=None):
        """
        :param entityClass:
        :param attributeGroupId:
        :param attributeId:
        :return:
        """
        # TODO: Remake entityClass
        uriAppend = '/belong/' + entityClass.lower() + 's'
        params = self.getQueryParams()

        if attributeGroupId:
            uriAppend += '/' + str(attributeGroupId)
            if attributeId:
                uriAppend += '/' + str(attributeId)

        response = self.handler.handle('GET', False, uriAppend, params)
        return self.make(response)
