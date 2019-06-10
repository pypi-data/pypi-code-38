from .base import Resource


class ClusterWideResource(Resource):
    """A cluster-wide Kubernetes resource, e.g. not scoped to a
    namespace.
    """
    cluster_wide = True

    @property
    def qualname(self):
        return self.name

    def setnamespace(self, *args, **kwargs):
        return self


ClusterWide = ClusterWideResource
