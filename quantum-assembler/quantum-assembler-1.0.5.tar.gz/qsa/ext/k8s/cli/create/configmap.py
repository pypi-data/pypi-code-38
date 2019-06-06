"""Create a new ``ConfigMap`` resource."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import Enable
from qsa.lib.cli import ArgumentList
from qsa.ext.k8s.services import ResourceCreateService


class CreateConfigMapCommand(Command):
    command_name = 'configmap'
    help_text = __doc__
    args = [
        Argument('namespace',
            help="specifies the unprefixed namespace."),
        Argument('name',
            help="the name of the ConfigMap."),
        Argument('-k', dest='keys', action='append', default=[], nargs='+',
            help="prefill the ConfigMap with the given keys/values."),
        ArgumentList('-l', dest='labels',
            help="specify labels for this resource."),
        ArgumentList('-a', dest='annotations',
            help="specify annotations for this resource."),
    ]
    codebase = ioc.class_property('core:CodeRepository')
    repo = ioc.class_property('k8s:Repository')

    def parse_keys(self, keys):
        cfg = {}
        for spec in keys:
            spec = str.join(' ', spec)
            key, value = str.split(spec, '=')
            cfg[key] = value
        return cfg

    def handle(self, quantum, project, codebase, ansible, args, deployment):
        args.keys = self.parse_keys(args.keys)
        service = ResourceCreateService(quantum, project, ansible, codebase,
            deployment)
        msg = f"created ConfigMap {args.name}"
        with self.codebase.commit(msg[0].upper()+msg[1:], noprefix=True):
            cfg = service.configmap(args.namespace, args.name, data=args.keys)
            cfg.settitle(msg)
            self.repo.add(cfg)
            quantum.persist()
