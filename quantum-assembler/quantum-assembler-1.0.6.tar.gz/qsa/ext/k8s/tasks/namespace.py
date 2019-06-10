from .base import KubernetesTask


class KubernetesNamespaceTask(KubernetesTask):
    ansible_ns = "k8s.namespaces"
    kind = 'Namespace'
    api_version = 'v1'
    annotation_domain = "net.quantumframework.org"
    label_domain = "net.quantumframework.org"
    cluster_wide = True

    def getdefaultspec(self):
        """Returns a default spec for this resource."""
        # Namespaces have no namespace
        spec = super().getdefaultspec()
        if 'namespace' in spec.metadata:
            del spec.metadata['namespace']
        return spec

    def setenvprefix(self, enable=True):
        """Sets the environment prefix to the relevant fields in
        the resource.
        """
        # Never prefix unbound resources
        if self.isunbound():
            return

        assert self.definition.metadata.name
        if enable:
            self.definition.metadata.name = f"{self.prefix_env}{self.name}"
        else:
            self.definition.metadata.name = str.replace(
                self.definition.metadata.name, self.prefix_env, '')
