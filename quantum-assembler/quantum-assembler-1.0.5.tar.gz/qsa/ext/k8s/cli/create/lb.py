"""Create a load balancer using ``Namespace`` and ``NetworkPolicy``
resources.
"""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Enable
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.ext.k8s.resources import ConfigMap
from qsa.ext.k8s.resources import Deployment
from qsa.ext.k8s.resources import LoadBalancer
from qsa.ext.k8s.resources import Namespace
from qsa.ext.k8s.resources import ServiceAccount
from qsa.ext.k8s.resources import Role
from qsa.ext.k8s.resources import RoleBinding


INGRESS_IMAGE = "quay.io/kubernetes-ingress-controller/nginx-ingress-controller:0.24.1"


class CreateLoadBalancerCommand(Command):
    command_name = 'lb'
    args = [
        Argument('namespace',
            help="specifies the namespace to create the load balancer in. Must be a DMZ"),
        Argument('name',
            help="the name of the load balancer. Must consist of alphanumeric characters."),
        ArgumentList('-p',
            help="protocols to handle using this loadbalancer."),
        Argument('--platform', required=True,
            help="specifies the platform on which the Kubernetes cluster is hosted."),
        Enable('--internal',
            help="indicates that the load balancer is internal."),
        Enable('--dynamic-ip',
            help="configure the load balancer IP from a template variable.")
    ]
    repository = ioc.class_property('k8s:Repository')
    template = ioc.class_property('template:Extension')
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, args, quantum):
        ns = self.repository.get(Namespace, args.namespace)
        resources = []

        # See https://github.com/kubernetes/ingress-nginx/tree/master/deploy/cloud-generic
        sa = ns.create(ServiceAccount, f'npa{args.name}')
        sa.settitle(f"created service account {sa.name} for load balancer {args.name}")
        resources.append(sa)

        # Create the default configmaps that are used by the controller.
        resources.append(ns.create(ConfigMap, f'{args.name}.config.nginx'))
        resources[-1].settitle(f"created configuration {resources[-1].name}")
        resources.append(ns.create(ConfigMap, f'{args.name}.config.tcp'))
        resources[-1].settitle(f"created configuration {resources[-1].name}")
        resources.append(ns.create(ConfigMap, f'{args.name}.config.udp'))
        resources[-1].settitle(f"created configuration {resources[-1].name}")

        # Create a role specific for this service account.
        manifest = self.template.render_to_yaml("k8s/addons/ingress-nginx/cloud-generic/role.yml.j2",
            ingress_controller_name=f"{ns.name}-{args.name}-{args.name}",
            namepace=ns.name, service_account=sa.name)
        role = ns.create(Role, sa.name, initial=manifest)
        role.settitle(f"created role {role.name}")
        resources.append(role)

        # Bind the service account to its own role.
        binding = ns.create(RoleBinding, sa.name)
        binding.setrole(role.name)
        binding.addsubjectfromresource(sa)
        binding.settitle(f"bound service account {sa.name} to role {role.name}")
        resources.append(binding)

        # Create the deployment to roll out the ingress-nginx controller
        ingress_args = [
            "/nginx-ingress-controller",
            "--configmap=$(POD_NAMESPACE)/$(NGINX_CONFIGMAP_NAME)",
            "--tcp-services-configmap=$(POD_NAMESPACE)/$(TCP_CONFIGMAP_NAME)",
            "--udp-services-configmap=$(POD_NAMESPACE)/$(UDP_CONFIGMAP_NAME)",
            "--publish-service=$(POD_NAMESPACE)/$(SERVICE_NAME)",
            "--annotations-prefix=nginx.ingress.kubernetes.io",
            f"--ingress-class={args.name}",
            f"--election-id={ns.name}-{args.name}",
            f"--watch-namespace={ns.name}"
        ]

        deployment = ns.create(Deployment, args.name)
        deployment.setserviceaccount(sa.name)
        deployment.template_metadata.annotations = {
            "prometheus.io/port": "10254",
            "prometheus.io/scrape": "true"
        }
        deployment.setreplicas(1)
        deployment.settitle(f"deployed ingress controller {deployment.name}")
        deployment.setselector({
            'app.kubernetes.io/name': args.name,
            'app.kubernetes.io/part-of': f'ingress-nginx-{args.name}'
        })
        container = deployment.createcontainer(INGRESS_IMAGE, args.name)
        container.setargs(ingress_args)
        container.setenvfieldref('POD_NAMESPACE', 'metadata.namespace')
        container.setenvfieldref('POD_NAME', 'metadata.name')
        container.setenv('NGINX_CONFIGMAP_NAME', f'{args.name}.config.nginx')
        container.setenv('TCP_CONFIGMAP_NAME', f'{args.name}.config.tcp')
        container.setenv('UDP_CONFIGMAP_NAME', f'{args.name}.config.udp')
        container.setenv('SERVICE_NAME', args.name)
        container.expose('http', 80)
        container.expose('https', 443)
        container.setlivenessprobe(success=1, failure=1, delay=10,
            period=10, timeout=10, probe={'httpGet': {'path': '/healthz', 'port': 10254, 'scheme': 'HTTP'}})
        container.setreadynessprobe(success=1, failure=1, delay=10,
            period=10, timeout=10, probe={'httpGet': {'path': '/healthz', 'port': 10254, 'scheme': 'HTTP'}})
        container.setsecuritycontext(privileged=True, drop=["ALL"], add=["NET_BIND_SERVICE"], user=33)
        resources.append(deployment)

        # Create a load balancer service
        svc = ns.create(LoadBalancer, args.name)
        svc.settitle(f"created load balancer service {args.name}")
        svc.setexternaltrafficpolicy('Local')
        svc.setport('http', 443)
        if args.dynamic_ip:
            svc.setloadbalancerip(f"{{{{ {args.name}_ip }}}}")
        deployment.addtoservice(svc)
        if args.platform == 'gke':
            if args.internal:
                svc.annotate('load-balancer-type', 'Internal', 'cloud.google.com')
        else:
            raise NotImplementedError
        resources.append(svc)

        # Set common labels for all resources
        with self.codebase.commit(f"Create load balancer {args.name}", noprefix=True):
            for resource in resources:
                resource.setpartof(f"ingress-nginx-{args.name}")
                self.repository.add(resource)

            # Bind the service account to the ingress-nginx-dmz role.
            binding = self.repository.get(RoleBinding, 'nginx-ingress-dmz',
                namespace=args.namespace, allow_create=False)
            binding.addsubjectfromresource(sa)
            self.repository.add(binding)
