from ms_sdk.Resourses.Mixins.FullResource import FullResourceMixin
from ms_sdk.Resourses.Resource import Resource


class DocumentsResource(Resource, FullResourceMixin):
    """
     Class DocumentsResource
     :method Document get(int id)
     :method Document first()
     :method Document[] all()
     :method Document update(id, data)
     :method Document create(data)
     :method Document|Document[] full(param = None)
     :method Document[] fullAll()
     :method Document fullById(int id)
     :method Document fullByCode(string code)
    """

    def getURI(self):
        return 'documents'
