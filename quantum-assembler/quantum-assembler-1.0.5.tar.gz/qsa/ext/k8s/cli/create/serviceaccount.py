"""Create a new ``ServiceAccount`` in a Kubernetes cluster in the
specified namespace."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import Enable
from qsa.lib.cli import ArgumentList
from qsa.ext.k8s.tasks import KubernetesServiceAccountTask


class CreateServiceAccountCommand(Command):
    command_name = 'serviceaccount'
    help_text = __doc__
    args = [
        Argument('namespace',
            help="a DNS-1123 compliant symbolic name identifying the Namespace."),
        Argument('name',
            help="specify the name of the service account."),
        Enable('--automount',
            help="Automount this token in pods."),
        Argument('--part-of',
            help="specifies the deployment this policy is part of.")
    ]
    resources = ioc.class_property('k8s:ResourceCreateService')
    repo = ioc.class_property('k8s:Repository')
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args):
        msg = f"Create ServiceAccount {args.name} in {args.namespace}"
        sa = self.resources.serviceaccount(args.namespace, args.name,
            automount=args.automount)
        if args.part_of:
            sa.setpartof(args.part_of)
        sa.tag(f'app.kubernetes.io/name:{args.name}')
        sa.settitle(f"created service account {args.name} in {args.namespace}")
        with self.codebase.commit(msg, noprefix=True):
            self.repo.add(sa)
            quantum.persist()
