"""Configure the cluster to deploy ``nginx-ingress``."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Enable
from qsa.ext.k8s.services import ResourceCreateService
from qsa.ext.k8s.tasks import RoleTask


NAMESPACE = 'ingress-nginx'
APP_NAME = 'ingress-nginx'
APP_MANIFEST = "https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml"


class CreateIngressNginxCommand(Command):
    command_name = 'ingress-nginx'
    help_text = __doc__
    args = [
        Enable('--disable-webhook')
    ]
    repo = ioc.class_property('ansible:TaskRepository')

    def handle(self, quantum, project, codebase, ansible, args, deployment):
        """Create a namespace to hold the ``ingress-nginx`` deployment
        and the custom resource definitions.
        """
        service = ResourceCreateService(quantum, project, ansible, codebase,
            deployment)
        try:
            with codebase.commit("Install ingress-nginx"):
                ansible = service.importmanifest(APP_MANIFEST,
                    name="install ingress-nginx ({kind})",
                    part_of='ingress-nginx',
                    tags=["deployment.quantumframework.org/env:global"],
                    exclude=['ConfigMap', 'Deployment'])

                # Most clusters will want to install multiple load balancers,
                # but the default ingress-nginx installation doesn't accomodate
                # for that. The permissions it configures for its service
                # account do no allow it to update any other configmap than
                # nginx-ingress-configuration. We patch it so that it can
                # update any configmap in the ingress-nginx namespace.
                role = self.repo.get(RoleTask, 'nginx-ingress-role')

                # Assert that the importmanifest() invocation correctly
                # imported the role.
                assert not role.isnew()

                role.addrule(groups=[""], resources=["configmaps"],
                    verbs=["get", "update"])
                role.persist()

                # Persist the history
                quantum.persist(codebase)
        except service.NamespaceExists:
            self.fail("Already installed.")
