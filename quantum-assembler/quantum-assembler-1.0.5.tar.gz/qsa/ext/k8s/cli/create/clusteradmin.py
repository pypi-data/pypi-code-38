"""Grant cluster admin privileges to the specified ``ServiceAccount``."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument


class CreateClusterAdminCommand(Command):
    command_name = 'clusteradmin'
    help_text = __doc__
    args = [
        Argument('name',
            help="the name of the ClusterRoleBinding resource."),
        Argument('namespace',
            help="specifies the prefixed namespace holding the service account."),
        Argument('account',
            help="specifies the name of the service account."),
        Argument('--part-of',
            help="specifies the deployment this policy is part of.")
    ]
    resources = ioc.class_property('k8s:ResourceCreateService')
    repo = ioc.class_property('k8s:Repository')
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args):
        binding = self.resources.clusterrolebinding(args.name,
            'cluster-admin', args.namespace, args.account, part_of=args.part_of)
        binding.settitle(f'created cluster admin binding {args.name}')
        with self.codebase.commit(f"Create cluster admin binding {args.name}", noprefix=True):
            self.repo.add(binding)
            quantum.persist()
