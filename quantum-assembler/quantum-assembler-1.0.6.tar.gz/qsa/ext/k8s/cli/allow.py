"""Create ``NetworkPolicy`` resources."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.lib.cli import Selectors


class AllowCommand(Command):
    command_name = 'allow'
    help_text = __doc__
    args = [
        Argument('namespace',
            help="specifies the namespace."),
        Argument('name',
            help="specifies the name of the network polcies in its namespace."),
        Argument('--dstns', required=False,
            help="specifies the destination namespace"),
        Selectors('--pod',
            help="specifies the source pod selectors. If omitted, the "
                "policy is applied to all pods in the namespace."),
        Selectors('--dstpod',
            help="specifies the destination pod selectors. If omitted, the "
                "policy is applied to all pods in the namespace."),
        Argument('--dstcidr', nargs='+',
            help="Destination CIDR."),
        ArgumentList('--tcp', type=int,
            help="the destination TCP port(s) of the traffic. The port is "
                "opened in both namespaces"),
        Argument('--part-of',
            help="specifies the deployment this policy is part of.")
    ]
    repo = ioc.class_property('k8s:Repository')
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args):
        args.pod = Selectors.parse(args.pod or {})
        args.dstpod = Selectors.parse(args.dstpod or {})
        args.dstcidr = ' '.join(args.dstcidr) if args.dstcidr else None

        # Get the source namespace and use their API
        # to create the resources. Namespace must exist.
        msg = f'Create network policy {args.name}'
        ns = self.repo.get('Namespace', args.namespace, allow_create=False)
        policy = ns.addpolicy(args.name)
        policy.settitle(msg.lower())

        if args.pod:
            policy.setpodselector(args.pod)
        if args.dstcidr or args.dstpod or args.dstns:
            policy.allowegress(tcp=args.tcp, cidr=args.dstcidr,
                namespace=args.dstns, pod=args.dstpod)
        if args.part_of:
            policy.setpartof(args.part_of)
        with self.codebase.commit(msg, noprefix=True):
            self.repo.add(policy)
            quantum.persist()
