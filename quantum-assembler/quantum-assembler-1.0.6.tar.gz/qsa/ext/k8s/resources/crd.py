from .clusterwide import ClusterWideResource
from .prefixable import Prefixable
from .persistable import Persistable


class CustomResourceDefinition(ClusterWideResource, Prefixable, Persistable):
    kind = 'CustomResourceDefinition'
    api_version = 'apiextensions.k8s.io/v1beta1'
    group = 'crd'
    stage = 'meta'
