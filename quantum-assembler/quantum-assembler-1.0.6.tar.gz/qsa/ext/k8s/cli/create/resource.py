"""Creates a resource of the specified type."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import Enable
from qsa.lib.cli import PartOf
from qsa.ext.k8s.resources import Deployment
from qsa.ext.k8s.resources import Role
from qsa.ext.k8s.resources import RoleBinding
from qsa.ext.k8s.resources import Service
from qsa.ext.k8s.resources import StatefulSet


RESOURCE_MAP = {
    'role': Role,
    'rolebinding': RoleBinding,
    'deployment': Deployment,
    'statefulset': StatefulSet,
    'svc': Service
}

class CreateResourceCommand(Command):
    command_name = 'resource'
    help_text = __doc__
    args = [
        Argument('kind', choices=list(RESOURCE_MAP.keys()),
            help="specifies the resource kind."),
        Argument('namespace',
            help="specifies the namespace to create the resource "
                 "in, without its environment prefix. If the "
                 "namespace does not have a prefix, make sure to "
                 "add the --noprefix argument."),
        Argument('name', nargs='+',
            help="the name of the resource. Template variables may "
                 "be used."),
        Enable('--noprefix',
            help="indicate that the namespace should not be prefixed."),
        PartOf('--part-of'),
    ]
    codebase = ioc.class_property('core:CodeRepository')
    repo = ioc.class_property('k8s:Repository')

    def handle(self, quantum, args):
        args.name = Argument.parsestring(args.name)
        Resource = RESOURCE_MAP[args.kind]
        ns = self.repo.get('Namespace', args.namespace)
        resource = ns.create(Resource, args.name)
        resource.settitle(f"created {Resource.kind} {args.name} in {args.namespace}")
        if args.part_of:
            resource.setpartof(args.part_of)
        msg = f"Create {Resource.kind} {args.name} in {args.namespace}"
        with self.codebase.commit(msg, noprefix=True):
            self.repo.add(resource)
            quantum.persist()
