"""Create a DMZ using ``Namespace`` and ``NetworkPolicy``
resources.
"""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Enable
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.ext.k8s.network import GKELoadbalancerBuilder
from qsa.ext.k8s.network import BaremetalLoadBalancerBuilder
from qsa.ext.k8s.resources import NetworkPolicy
from qsa.ext.k8s.resources import PodSecurityPolicy
from qsa.ext.k8s.resources import Role
from qsa.ext.k8s.resources import RoleBinding


class CreateDemilitarizedZoneCommand(Command):
    command_name = 'dmz'
    builders = {
        'gke': GKELoadbalancerBuilder,
        'baremetal': BaremetalLoadBalancerBuilder
    }
    codebase = ioc.class_property('core:CodeRepository')
    repository = ioc.class_property('k8s:Repository')
    resources = ioc.class_property('k8s:ResourceCreateService')
    template = ioc.class_property('template:Extension')
    args = [
        Argument('name', help="the name of the DMZ."),
        Argument('--addr',
            help="the IP address of the load balancer, if applicable."),
        ArgumentList('-e', dest='environments',
            help="the environments to deploy the DMZ in."),
        Argument('--part-of',
            help="specifies the deployment this policy is part of.")
    ]

    def handle(self, args, quantum):
        if not args.environments:
            self.fail("Specify at least one environment using the -e parameter")
        msg = f"Create DMZ {args.name}"
        msg += f' ({", ".join(args.environments)})'
        with self.codebase.commit(msg, noprefix=True):
            self.create_namespace(args)
            quantum.persist()

    def create_namespace(self, args):
        base_name = f'dmz{args.name}'
        msg = f"created namespace '{base_name}' for DMZ {args.name}"
        ns = self.resources.namespace(base_name, isdmz=True, unbound=True,
            environments=args.environments, msg=msg, part_of=base_name)\
            .label('part-of', base_name, 'app.kubernetes.io')\
            .label('component', 'dmz', 'app.kubernetes.io')

        # The ingress-nginx controller needs access to the Kubernetes
        # management API at https://kubernetes.default:443. This service
        # resolves to the cluster management IP, but we do not know it
        # at compile time so we inject it as a variable.
        policy = self.repository.get(NetworkPolicy, 'default-allow',
            namespace=base_name)
        policy.allowegress(cidr='{{ K8S_CLUSTER_MANAGEMENT_IP }}/32',
            tcp=[443])
        policy.setpartof(args.part_of or f'dmz{args.name}')
        self.repository.add(policy)

        # Create a PodSecurityPolicy for the ingress controller.
        policy = ns.create(PodSecurityPolicy, f'{ns.base_name}-ingress-nginx')
        policy.settitle(f"configured pod security for DMZ {args.name}")
        policy.on_bound() # TODO
        policy.allowcap('NET_BIND_SERVICE')
        policy.forbidcap('ALL')
        policy.allowescalation(True)
        policy.setdefaults()
        policy.setpartof(args.part_of or f'dmz{args.name}')
        self.repository.add(policy)

        # Create the nginx-ingress-dmz role for all controllers deployed
        # in this DMZ.
        manifest = self.template.render_to_yaml(
            'k8s/addons/ingress-nginx/cluster-wide/cluster-role.yml.j2',
            namespace=base_name
        )
        role = ns.create(Role, manifest.metadata.name, initial=manifest)
        role.settitle(f"created ingress role for DMZ {args.name}")
        role.setpartof(args.part_of or f'dmz{args.name}')
        role.addrule(['policy'], ['podsecuritypolicies'], ['use'], [f'{ns.name}-ingress-nginx'])
        self.repository.add(role)

        #  Create a RoleBinding, but without any subjects. These will be added
        # when load balancers are created.
        binding = ns.create(RoleBinding, name='nginx-ingress-dmz')
        binding.settitle(f"created role binding for load balancers in DMZ {args.name}")
        binding.setpartof(args.part_of or f'dmz{args.name}')
        binding.setrole(role.name)
        self.repository.add(binding)

        return base_name, ns
