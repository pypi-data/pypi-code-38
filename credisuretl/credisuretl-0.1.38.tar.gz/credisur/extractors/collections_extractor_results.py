from credisur.models import Collections
from credisur.datastructures import HashOfLists

class CollectionsExtractorResults:

    def __init__(self):
        self.collections = Collections()
        self.collections_for_customers = HashOfLists()
        self.errors = []


    def append_to_collections(self, collection):
        self.collections.append(collection)

    def append_to_collections_for_customers(self, customer, collection):
        self.collections_for_customers.append(customer, collection.to_dict())

    def get_errors(self):
        return self.errors

    def get_collections(self):
        return self.collections

    def get_collections_for_customers(self):
        return self.collections_for_customers
                