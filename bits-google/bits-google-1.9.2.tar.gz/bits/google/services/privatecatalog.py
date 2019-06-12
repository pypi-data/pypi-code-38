"""Private Catalog API class file."""

from bits.google.services.base import Base
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession


class PrivateCatalog(Base):
    """PrivateCatalog class."""

    def __init__(self, credentials, api_key):
        """Initialize a class instance."""
        self.privatecatalog_alpha = build(
            'cloudprivatecatalog',
            'v1alpha1',
            credentials=credentials,
            discoveryServiceUrl='https://cloudprivatecatalog.googleapis.com/$discovery/rest?version=v1alpha1&key=%s' % (
                api_key
            )
        )

        self.catalogproducer = build('cloudprivatecatalogproducer', 'v1beta1', credentials=credentials)
        self.catalog = build('cloudprivatecatalog', 'v1beta1', credentials=credentials)

    def get_catalogs(self, resource):
        """Return a list of catalogs."""
        catalogs = self.catalogproducer.catalogs()
        request = catalogs.list(parent=resource)
        return self.get_list_items(catalogs, request, 'catalogs')

    # def delete_catalog(self, resource):
    #     """Return a list of catalogs."""
    #     print(dir(self.privatecatalog_alpha.catalogs()))
    #     return self.privatecatalog_alpha.catalogs().delete(resource=resource).execute()

    def get_products(self, parent):
        """Return a list of catalogs."""
        products = self.catalogproducer.catalogs().products()
        request = products.list(parent=parent)
        return self.get_list_items(products, request, 'products')
