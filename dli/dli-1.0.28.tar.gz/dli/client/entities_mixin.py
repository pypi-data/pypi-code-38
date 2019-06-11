from dli.client.collection_functions import CollectionFunctions
from dli.client.dataset_mixin import DatasetMixin
from dli.client.package_functions import PackageFunctions


"""
Aggregate mixin of catalogue entities
"""
class EntityMixin(CollectionFunctions, PackageFunctions, DatasetMixin):
    pass