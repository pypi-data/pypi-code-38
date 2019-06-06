"""Create a new Namespace in a Kubernetes cluster."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import Enable
from qsa.lib.cli import ArgumentList
from qsa.ext.k8s.tasks import KubernetesNamespaceTask
from qsa.ext.k8s.tasks import KubernetesNetworkPolicyTask
from qsa.ext.k8s.services import ResourceCreateService


class CreateNamespaceCommand(Command):
    command_name = 'ns'
    help_text = __doc__
    args = [
        Argument('name',
            help="a DNS-1123 compliant symbolic name for the Namespace."),
        ArgumentList('-e', dest='environments',
            help="specify the environments in which this Namespace is created."),
        Enable('--isdmz',
            help="indicates that the namespace is a DMZ."),
        Enable('--unbound',
            help="do not bind this namespace to a specific environment."),
        ArgumentList('-l', dest='labels',
            help="specify labels for this resource."),
        ArgumentList('-a', dest='annotations',
            help="specify annotations for this resource."),
    ]
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, project, codebase, ansible, args, deployment):
        service = ResourceCreateService(quantum, project, ansible, codebase,
            deployment)
        try:
            msg = f"Create namespace {args.name} in {project.display_name}"
            with self.codebase.commit(msg, noprefix=True):
                ns = service.namespace(args.name, isdmz=args.isdmz,
                    unbound=args.unbound, environments=args.environments,
                    labels=args.labels, annotations=args.annotations)
                quantum.persist()
        except service.NamespaceExists:
            self.fail(f"Namespace exists: {args.name}")
