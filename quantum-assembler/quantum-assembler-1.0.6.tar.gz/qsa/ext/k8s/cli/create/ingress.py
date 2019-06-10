"""Creates a new ``Ingress`` for the specified load
balancer.
"""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.ext.k8s.resources import Ingress
from qsa.ext.k8s.resources import Namespace


class CreateIngressCommand(Command):
    command_name = 'ingress'
    help_text = __doc__
    args = [
        Argument('namespace',
            help="specifies the namespace. Must be a DMZ."),
        Argument('name',
            help="the name of the Ingress resource."),
        Argument('--load-balancer', required=True,
            help="specifies the load balancer to associate the ingress to."),
        Argument('--ca-issuer', nargs='+',
            help="specifies the cluster issuer for this ingress.")
    ]
    repository = ioc.class_property('k8s:Repository')
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args):
        ns = self.repository.get(Namespace, args.namespace)
        ingress = ns.create(Ingress, args.name)
        ingress.setloadbalancer(args.load_balancer)
        ingress.setpartof(args.load_balancer)
        if args.ca_issuer:
            ingress.setcaissuer(str.join(' ', args.ca_issuer))
        msg = f"Created ingress '{args.name}'"
        with self.codebase.commit(msg, noprefix=True):
            self.repository.add(ingress)
            quantum.persist()
