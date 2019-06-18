from ms_sdk.Resourses.Resource import Resource
from ms_sdk.Resourses.Mixins.FullResource import FullResourceMixin


class ProductsResource(Resource, FullResourceMixin):
    """
    Class ProductsResource
    :method Product get(int id)
    :method Product first()
    :method Product[] all()
    :method Product update(id, data)
    :method Product create(data)
    :method Product|Product[] full(param = None)
    :method Product[] fullAll()
    :method Product fullById(int id)
    :method Product fullByCode(string code)
    """

    def getURI(self):
        return 'products'
