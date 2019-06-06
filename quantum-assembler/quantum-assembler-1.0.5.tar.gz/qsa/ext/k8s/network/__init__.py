import os

import ioc

from qsa.ext.k8s.resources import ClusterRoleBinding
from qsa.ext.k8s.resources import NetworkPolicy


NGINX_INGRESS = "https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml"


class BaseLoadbalancerBuilder:
    resources = ioc.class_property('k8s:ResourceCreateService')
    repo = ioc.class_property('k8s:Repository')
    deployments = ioc.class_property('deployment:Extension')

    @classmethod
    def build(cls, *args, **kwargs):
        builder = cls(*args, **kwargs)
        return builder.create()

    def __init__(self, name, addr, ranges, unbound=True, internal=False, ports=None, environments=None):
        self.name = name
        self.addr = addr
        self.ranges = ranges
        self.internal = internal
        self.ports = ports or []
        self.environments = environments or []

    def getenvironments(self):
        return self.environments

    def create(self):
        raise NotImplementedError

    def isunbound(self):
        """Return a boolean indicating if the load balancer is not
        bound to any environment.
        """
        return self.environment == 'global'


class BaremetalLoadBalancerBuilder(BaseLoadbalancerBuilder):
    """Simply creates a ``Service`` of type ``NodePort``."""

    def create(self):
        """Add the necessary tasks to the Ansible playbooks to
        create the load balancer.
        """
        base_name, ns = self.create_namespace()
        msg = 'created node port load balancer'
        nodeport = self.resources.nodeport(base_name, f'{base_name}-lb', msg)\
            .setloadbalancerip(self.addr)\
            .label('part-of', base_name, 'app.kubernetes.io')\
            .label('component', 'dmz', 'app.kubernetes.io')\
            .setselector('app.kubernetes.io/part-of', 'ingress-nginx')\
            .setselector('app.kubernetes.io/name', 'ingress-nginx')\
            .setportsfromstring(self.ports)\
            .setunbound()

        self.repo.add(nodeport)


class GKELoadbalancerBuilder(BaseLoadbalancerBuilder):
    """Constructs the Ansible tasks to build a load balancer on Google
    Kubernetes Engine (GKE).
    """

    def create(self):
        """Add the necessary tasks to the Ansible playbooks to
        create the load balancer.
        """
        base_name, ns = self.create_namespace()
        varname = f'LB_{str.upper(self.name).replace("-", "_")}_IP'
        if self.internal:
            msg = f"created internal load balancer '{base_name}' (GKE)"
            lb = self.resources.loadbalancer(base_name, f'{base_name}-lb', msg)\
                .setloadbalancerip(f"{{{{ {varname} }}}}")\
                .setsourceranges(self.ranges)\
                .annotate('load-balancer-type', 'Internal', 'cloud.google.com')\
                .label('part-of', base_name, 'app.kubernetes.io')\
                .label('part-of', base_name, 'app.kubernetes.io')\
                .label('component', 'dmz', 'app.kubernetes.io')\
                .setselector('app.kubernetes.io/part-of', 'ingress-nginx')\
                .setselector('app.kubernetes.io/name', 'ingress-nginx')\
                .label('app', base_name)\
                .setportsfromstring(self.ports)\
                .setenvironments(self.environments)

            # FIXME
            #lb._manifest.spec.selector = {'app': base_name}
        else:
            msg = f"created external load balancer '{base_name}' (GKE)"
            lb = self.resources.loadbalancer(base_name, f'{base_name}-lb', msg)\
                .setloadbalancerip(f"{{{{ {varname} }}}}")\
                .setexternaltrafficpolicy('Local')\
                .label('part-of', base_name, 'app.kubernetes.io')\
                .label('part-of', base_name, 'app.kubernetes.io')\
                .label('component', 'dmz', 'app.kubernetes.io')\
                .setselector('app.kubernetes.io/part-of', 'ingress-nginx')\
                .setselector('app.kubernetes.io/name', 'ingress-nginx')\
                .label('app', base_name)\
                .setportsfromstring(self.ports)\
                .setenvironments(self.environments)

        self.repo.add(lb)
        self.create_ingress_controller(ns, base_name)
        return

    def create_ingress_controller(self, ns, base_name):
        # Get the current ClusterRoleBinding so we can merge the existing
        # subject with it.
        namespace = ns.namespace
        old = self.repo.get(ClusterRoleBinding,
            'nginx-ingress-clusterrole-nisa-binding')

        # Ennsure that the ClusterRole is present and that the ingress-nginx
        # service account for this namespace is selected. Get the new subject
        # and add it to the existing binding.
        only = ['ClusterRole']
        if old.isnew():
            only.append('ClusterRoleBinding')
        resources = self.resources.importmanifest(NGINX_INGRESS,
            name=f"configured cluster for ingress-nginx ({{kind}})", only=only,
            force_namespace=base_name)
        assert resources.all(lambda x: x.kind in ('ClusterRole', 'ClusterRoleBinding'))
        resources.label('component', 'dmz', 'app.kubernetes.io')\
            .setunbound(True)

        # Remove the subject and declare one for each environment
        binding = self.repo.get(ClusterRoleBinding,
            f'nginx-ingress-clusterrole-nisa-binding')
        if old.isnew():
            binding.popsubject('ingress-nginx', 'nginx-ingress-serviceaccount', None)
        for env in self.environments:
            sub = {
                'kind': 'ServiceAccount',
                'name': "nginx-ingress-serviceaccount",
                'namespace': ns.getenvname(env)
            }
            binding.addsubject(sub)

        binding.tag('always')
        self.repo.add(binding)

        # Import nginx-ingress into the namespace. Retrieve the deployment
        # and set some parameters for use with multiple ingress controllers.
        resources = self.resources.importmanifest(NGINX_INGRESS,
            name=f"created ingress for DMZ '{base_name}' ({{kind}})",
            exclude=['Namespace', 'ClusterRole', 'ClusterRoleBinding'],
            force_namespace=base_name)
        resources.label('component', 'dmz', 'app.kubernetes.io')\
            .label('part-of', base_name, 'app.kubernetes.io')\
            .setenvironments(self.environments)\
            .persist(self.repo)

        election_id = bytes.hex(os.urandom(3))
        task = resources.get(f'{base_name}-nginx-ingress-controller')
        task.label('app', base_name)
        container = task.getcontainer('nginx-ingress-controller')
        container.setenv('NGINX_INGRESS_CLASS', base_name)
        container.setenv('K8S_NAMESPACE_PREFIX', "{{ K8S_NAMESPACE_PREFIX }}")
        container.setargs([
            '/nginx-ingress-controller',
            '--annotations-prefix=nginx.ingress.kubernetes.io',
            f'--election-id=lb-{election_id}',
            f'--ingress-class=$(K8S_NAMESPACE_PREFIX){base_name}',
            f'--publish-service=$(POD_NAMESPACE)/{base_name}-lb',
            '--configmap=$(POD_NAMESPACE)/nginx-configuration',
            '--tcp-services-configmap=$(POD_NAMESPACE)/tcp-services',
            '--udp-services-configmap=$(POD_NAMESPACE)/udp-services'
        ])

        # As with the ClusterRoleBinding, ensure that also the
        # RoleBinding is assigned to the service account.
        binding = resources.get(f'{base_name}-nginx-ingress-role-nisa-binding')
        binding.setenvironments(self.environments)

        # FIXME: Find out why the namespace is not correctly set at
        # this point
        if not binding.isunbound() and binding.prefix not in binding.namespace:
            binding.namespace = f'{binding.prefix}{binding.namespace}'

        assert not binding.isunbound()

        subject = binding.getsubject('ingress-nginx', 'nginx-ingress-serviceaccount')
        subject.namespace = ns.getresourcenamespace(base_name)
        self.repo.add(binding)

        # The ingress-nginx controller uses ConfigMap resources to update
        # its state. By default, the name of the allowed configmap is hard-coded
        # in its Role; however QSA uses a different naming scheme and we
        # don't know the name beforehand. Since we deploy only one LB
        # to a single namespace, it's safe to grant it update permission
        # on all configmaps in that namespace.
        role = resources.get(f'{base_name}-nginx-ingress-role')
        for rule in role.rules:
            if 'resourceNames' not in rule:
                continue
            if 'configmaps' not in rule.resources:
                continue
            rule.pop('resourceNames')
            break
        else:
            raise RuntimeError("ConfigMap rule not found.")
        self.repo.add(role)

        resources.persist(self.repo)
