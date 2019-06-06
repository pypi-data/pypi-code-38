"""Create ``NetworkPolicy`` resources between two namespaces."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.lib.cli import Selectors


class CreatePairNetworkPolicyCommand(Command):
    command_name = 'pairnetworkpolicy'
    help_text = __doc__
    args = [
        Argument('name',
            help="specifies the name of the network polcies in both "
                "namespaces."),
        Argument('--srcns', required=True,
            help="specifies the source namespace"),
        Argument('--dstns', required=True,
            help="specifies the destination namespace"),
        Selectors('--srcpod',
            help="specifies the source pod selectors. If omitted, the "
                "policy is applied to all pods in the namespace."),
        Selectors('--dstpod',
            help="specifies the destination pod selectors. If omitted, the "
                "policy is applied to all pods in the namespace."),
        ArgumentList('--dstport',
            help="the destination port of the traffic. The port is opened "
                "in both namespaces"),
        ArgumentList('--tcp', type=int,
            help="the destination TCP port(s) of the traffic. The port is "
                "opened in both namespaces"),
        Argument('--part-of',
            help="specifies the deployment this policy is part of.")
    ]
    repo = ioc.class_property('k8s:Repository')
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args):
        args.dstport = Argument.parseports(args.dstport)
        args.dstpod = Selectors.parse(args.dstpod or {})
        args.srcpod = Selectors.parse(args.srcpod or {})

        # Get the source and destination namespace and use their API
        # to create the resources. Both namespaces must exist.
        msg = f'Create mirrored network policy {args.name}'
        srcns = self.repo.get('Namespace', args.srcns, allow_create=False)
        dstns = self.repo.get('Namespace', args.dstns, allow_create=False)
        srcpolicy = srcns.addpolicy(args.name)
        dstpolicy = dstns.addpolicy(args.name)

        # Set the selectors for the pods on both sides.
        srcpolicy.setpodselector(args.srcpod)\
            if args.srcpod\
            else srcpolicy.setpodselector({})
        dstpolicy.setpodselector(args.dstpod)\
            if args.dstpod\
            else srcpolicy.setpodselector({})

        # Set egress rule for srcns, ingress rule for dstns.
        srcpolicy.allowegress(namespace=dstns.qualname, ports=args.dstport,
            pod=args.dstpod, tcp=args.tcp)
        dstpolicy.allowingress(namespace=srcns.qualname, ports=args.dstport,
            pod=args.srcpod, tcp=args.tcp)

        if args.part_of:
            srcpolicy.setpartof(args.part_of)
            dstpolicy.setpartof(args.part_of)

        srcpolicy.settitle(msg.lower())
        dstpolicy.settitle(msg.lower())
        with self.codebase.commit(msg, noprefix=True):
            self.repo.add(srcpolicy)
            self.repo.add(dstpolicy)
            quantum.persist()
