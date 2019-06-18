from ms_sdk.Resourses.Resource import Resource


class CatalogItemsResource(Resource):
    """
    Class CatalogItemsResource
    :method CatalogItem get(int id):
    :method CatalogItem first():
    :method CatalogItem[] all():
    :method CatalogItem update(id, data):
    :method CatalogItem create(data):
    """

    def getURI(self):
        return 'catalogitems'
