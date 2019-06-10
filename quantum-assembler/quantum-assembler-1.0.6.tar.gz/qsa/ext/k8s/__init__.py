import copy
import os
import glob
import sys

import ioc

import qsa.lib.cli
from qsa.lib.datastructures import DTO
from qsa.ext.base import BaseExtension
from .const import TAG_DEPLOYMENT_ENV
from .const import TAG_DEPLOYMENT_PHASE
from .cli import AddManifestCommand
from .cli import AllowCommand
from .cli import CreateCommand
from .cli import ImportCommand
from .model import Cluster
from .model import Secret
from .repo import KubernetesRepository
from .schema import ConfigSchema
from .services import ResourceCreateService
from .tasks import KubernetesConfigMapTask
from .tasks import DeploymentTask as KubernetesDeploymentTask
from .tasks import ServiceTask as KubernetesServiceTask


class AnnotationController:

    def __init__(self, domain, annotations):
        self.annotations = annotations

    def get(self, path):
        return self.annotations[f'{self.domain}/{path}']


class Extension(BaseExtension):
    name = 'k8s'
    command_name = 'k8s'
    weight = 11.0
    schema_class = ConfigSchema
    codebase = ioc.class_property('core:CodeRepository')
    templates = ioc.class_property('template:Extension')
    subcommands = [
        {
            'name': 'initcluster',
            'args': [
                ('name', {}),
                ('--context', {})
            ]
        },
        {
            'name': 'createenv',
            'args': [
                {'dest': 'name'},
                ('--alias', {}),
                ('--production', {'action': 'store_true'}),
                ('--allow-purge', {'action': 'store_true'})
            ]
        },
        {
            'name': 'whitelist',
            'args': [
                {'dest': 'namespace'},
                {'dest': 'name'},
                ('--srcns', {}),
                ('--srcpod', {}),
                ('--srcport', {'action': 'append', 'default': []}),
                ('--srcip', {}),
                ('--dstns', {'action': 'append', 'dest': 'dstns'}),
                ('--dstpods', {}),
                ('--dstport', {'action': 'append', 'default': []}),
                ('--dstip', {'action': 'append', 'default': []}),
                ('--ingress-port', {'action': 'append', 'default': [], 'dest': 'ingress_ports'}),
                ('--ingress-cidr', {'action': 'append', 'default': [], 'dest': 'ingress_ranges'}),
                ('--noprefix', {'action': 'store_true'})
            ]
        },
        AddManifestCommand,
        AllowCommand,
        CreateCommand,
        ImportCommand,
    ]

    def setup(self, project, ansible, codebase, deployment):
        service = ResourceCreateService(self.quantum, project, ansible,
            codebase, deployment)
        self.provide_class(service)
        ioc.provide('k8s:Repository', KubernetesRepository())

    def handle_whitelist(self, args, codebase):
        """Configures the firewall rules for the specified namespace."""
        cluster = Cluster(self.quantum, self.spec.k8s.cluster)
        label = "networking.quantumframework.org/vlan"
        with codebase.commit(f"Configure firewall for namespace '{args.namespace}'"):
            ns = cluster.getns(args.namespace)
            ingress = DTO(
                ports=args.ingress_ports,
                ranges=args.ingress_ranges
            )
            if any([args.dstip, args.dstns, args.dstpods, args.dstport]):
                if args.dstpods and not args.dstns:
                    self.fail("The --dstns is required with --dstpod.")
                if args.dstip or args.dstns or args.dstport:
                    ns.allowdst(args.name, cidr=args.dstip, namespaces=args.dstns,
                        pod=args.srcpod, ports=args.dstport, ingress=ingress,
                        noprefix=args.noprefix)
                if args.dstpods:
                    raise NotImplementedError
            self.quantum.persist(codebase)
            return

    def handle_createenv(self, args, codebase, deployment):
        """Configures an environment for the infrastructure."""
        with self.codebase.commit(f"Create '{args.name}' environment"):
            env, created = deployment.createenv(args.name,
                alias=args.alias, isproduction=args.production,
                allow_purge=args.allow_purge)
            env.setproduction(args.production)
            self.quantum.persist()

    def handle_initcluster(self, codebase, args):
        """Initial configuration of a Kubernetes cluster."""
        schema = self.schema_class.getforload()
        defaults = schema.defaults({
            'k8s': {
                'cluster': {
                    'name': args.name,
                    'context': args.context
                }
            }
        })
        with self.codebase.commit("Initialize Kubernetes cluster configuration", noprefix=True):
            self.quantum.init('k8s+cluster', args.name,
                codebase=self.codebase, force=True)
            self.spec = defaults
            self.quantum.persist()

    def handle(self, codebase, vaults, ansible):
        typname = self.quantum.get('project.type')

        if typname == 'k8s+deployment':
            pass

        if typname == 'k8s+cluster':
            # Ensure that we have a vault to store the cluster-wide
            # secrets in.
            #if not codebase.exists('vault/global.aes'):
            #    with codebase.commit("Create vaults for cluster secrets"):
            #        self.assembler.notify('vault_required')
            #        vaults.create(codebase, 'global')
            #spec = self.quantum.get('k8s.cluster', None)
            #if spec is None:
            #    self.fail("Quantumfile corrupted: no k8s.cluster entry.")
            #cluster = Cluster(self.quantum, spec)
            #buf = ''
            #namespaces = cluster.namespaces | cluster.dmz
            #for n, name in enumerate(sorted(namespaces)):
            #    ns = cluster.getns(name)
            #    buf += '---\n'
            #    buf += str(ns)

            # Ensure that vars for environments exist.
            #with codebase.commit("Ensure that variables exist"):
            #    codebase.mkdir('ops/ansible/defaults')
            #    fn = codebase.abspath(f'ops/ansible/defaults/global.yml')
            #    if not codebase.exists(fn):
            #        codebase.write(fn, '---\n{}')
            #    for env in self.quantum.get('deployment.environments', {}).values():
            #        fn = codebase.abspath(f'ops/ansible/defaults/{env.name}.yml')
            #        if codebase.exists(fn):
            #            continue
            #        codebase.write(fn, '---\n{}')

            import os

            from .ansible import TaskSequence
            from .ansible import TopLevelTaskSequence
            with self.codebase.commit("Create Kubernetes playbooks"):
                base_dir = 'ops/ansible'
                self.codebase.mkdir('ops/ansible/tasks/k8s')

                # Render a task to deploy the secrets to the cluster.
                ctx = {}
                self.templates.render_to_file('ci/ansible/tasks/k8s.secrets.yml.j2',
                    'ops/ansible/tasks/k8s/secrets.yml', **ctx)

                # TODO: Determine if we should render.
                main = TopLevelTaskSequence(f'{base_dir}/tasks/k8s')
                stages = [
                    'meta',
                    'config',
                    'cluster',
                    'iam',
                    'network',
                    'security',
                    'connectivity',
                    'applications',
                ]
                for i, dirname in enumerate(stages):
                    # FIXME: Ugly award
                    if i == 2:
                        main.include_tasks('secrets.yml')
                    if not os.path.exists(os.path.join('ops/ansible/templates/k8s', dirname)):
                        print(f"{dirname} does not exist")
                        continue
                    seq = TaskSequence(base_dir, dirname)
                    seq.render()
                    main.include_tasks(f'{dirname}.yml')
                main.render()

    def on_setup_makefile(self, make):
        """Create targets to deploy to each environment and stage."""
        typname = self.quantum.get('project.type')
        if typname != 'k8s+cluster':
            return
        make.setvariable('ANSIBLE_DEPLOYER_IMAGE',
            "docker.io/quantumframework/agent-ansible-k8s:latest")
        make.setvariable('ANSIBLE_SECRETS_MOUNT', '/var/run/secrets/secrets.quantumframework.org/')
        make.setvariable('ANSIBLE_KUBECONFIG', 'kubeconfig.conf')
        make.setvariable('ANSIBLE_MOUNTS',
            '-v $(shell pwd)/env:$(ANSIBLE_SECRETS_MOUNT)/pgp:ro -v $(shell pwd):/app')
        make.setvariable('ANSIBLE_ENV', '-e KUBECONFIG=/app/env/kubeconfig.conf')
        make.setvariable('ANSIBLE_DEPLOY',
            'docker run -it $(ANSIBLE_MOUNTS)\\\n\t$(ANSIBLE_ENV) -w /app $(ANSIBLE_DEPLOYER_IMAGE)\\\n\tansible-playbook $(ANSIBLE_PLAYBOOK)')
        make.setvariable('ANSIBLE_PLAYBOOK', 'ops/ansible/main.yml -e @vault/$(K8S_DEPLOYMENT_ENV).aes', True)
        make.setvariable('ANSIBLE_TAGS', f'-t {TAG_DEPLOYMENT_ENV}:$(K8S_DEPLOYMENT_ENV)', True)
        make.setvariable('ANSIBLE_DEFAULTS', '-e @ops/ansible/defaults/$(K8S_DEPLOYMENT_ENV).yml')
        make.setvariable('ANSIBLE_ARGS', '')
        make.setvariable('K8S_NAMESPACE_PREFIX', '', True)
        make.setvariable('K8S_DEPLOYMENT_ENV', 'global', True)

        target = make.target('ansible-deploy')
        target.execute(
            f'$(ANSIBLE_DEPLOY) $(ANSIBLE_TAGS) $(ANSIBLE_DEFAULTS)\\\n\t\t'
            f'-e "K8S_NAMESPACE_PREFIX=$(K8S_NAMESPACE_PREFIX)"\\\n\t\t'
            f'-e "K8S_DEPLOYMENT_ENV=$(K8S_DEPLOYMENT_ENV)" $(ANSIBLE_ARGS)'
        )

        target = make.target('ansible-deploy-bootstrap')
        target.execute(f'make ansible-deploy\\\n\t\tANSIBLE_TAGS="-t {TAG_DEPLOYMENT_PHASE}:bootstrap"\\\n\t\tK8S_DEPLOYMENT_ENV=global')
        target = make.target('ansible-deploy-global')
        target.execute(f'make ansible-deploy\\\n\t\tANSIBLE_TAGS="-t {TAG_DEPLOYMENT_ENV}:global"\\\n\t\tK8S_DEPLOYMENT_ENV=global')


        deploy = make.target('ansible-deploy-all')
        deploy.execute(f'make ansible-deploy-bootstrap')
        deploy.execute(f'make ansible-deploy-global')
        for env in self.quantum.get('deployment.environments').values():
            target = make.target(f'ansible-deploy-{env.name}')
            target.execute(
                f'make ansible-deploy\\\n\t\t'
                f'K8S_DEPLOYMENT_ENV={env.name}\\\n\t\t'
                f'K8S_NAMESPACE_PREFIX=ns{env.alias}'
            )
            deploy.execute(f'make ansible-deploy-{env.name}')


    def on_ansible_playbook_render(self, ctx):
        typname = self.quantum.get('project.type')
        if typname != 'k8s+cluster':
            return
        base_tasks = [
            {'name': "Bootstrap core cluster services", "path": "k8s/bootstrap.yml"},
            {'name': "Deploy namespaces", "path": "k8s/namespaces.yml"},
            {'name': "Deploy custom resource definitions",
              "path": "k8s/crd.yml"},
            {'name': "Deploy cluster-wide resources",
              "path": "k8s/cluster.yml"},
            {'name': "Deploy persistent volume claims",
              "path": "k8s/volumes.yml"},
            {'name': "Deploy DNS",
              "path": "k8s/dns.yml"},
            {'name': "Deploy endpoints",
              "path": "k8s/endpoints.yml"},
            {'name': "Deploy configuration",
              "path": "k8s/config.yml"},
            {'name': "Deploy IAM",
              "path": "k8s/iam.yml"},
            {'name': "Deploy network security",
              "path": "k8s/network.yml"},
            {'name': "Deploy pod security",
              "path": "k8s/pod-security-policies.yml"},
            {'name': "Deploy RBAC",
              "path": "k8s/rbac.yml"},
            {'name': "Deploy CA",
              "path": "k8s/ca.yml"},
            {'name': "Deploy Monitoring",
              "path": "k8s/monitoring.yml"},
            {'name': "Deploy Maintenance",
              "path": "k8s/maintenance.yml"},
            {'name': "Deploy Quota",
              "path": "k8s/quota.yml"},
            {'name': "Deploy Applications",
              "path": "k8s/deployments.yml"},
            {'name': "Deploy Ingress Controllers",
              "path": "k8s/ingress.yml"},
            {'name': "Deploy Load Balancers",
              "path": "k8s/loadbalancers.yml"},
        ]
        ctx['ANSIBLE_INCLUDE_PLAYBOOKS'] = tasks = []
        for t in base_tasks:
            if not self.codebase.exists(f'ops/ansible/{t["path"]}'):
                continue
            tasks.append(t)
