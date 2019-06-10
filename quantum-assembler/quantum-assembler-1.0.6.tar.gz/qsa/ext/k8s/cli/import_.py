"""Import a Kubernetes manifest."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.ext.k8s.services import ResourceCreateService


class ImportCommand(Command):
    command_name = 'import'
    help_text = __doc__
    args = [
        Argument('name', help="symbolic name for the imported resource set."),
        Argument('-u', dest='url',
            help="import manifest from the given URL."),
        Argument('-m,', dest='name_template', nargs='+', default=[],
            help="name template for the generated tasks."),
        Argument('-X', '--disable-firewall', action='store_true',
            help="do not create network policies for namespaces."),
        Argument('--exclude,', dest='exclude', action='append', default=[],
            help="exclude resources from the import."),
    ]
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args, project, ansible, deployment):
        with self.codebase.commit(f"install {args.name}"):
            service = ResourceCreateService(quantum, project, ansible,
                self.codebase, deployment)
            try:
                service.importmanifest(args.url,
                    name=str.join('', args.name_template)\
                        or f"install {args.name} ({{kind}})",
                    part_of=args.name, exclude=args.exclude,
                    disable_firewall=args.disable_firewall,
                    tags=["deployment.quantumframework.org/env:global"])

                # Persist the history
                quantum.persist(self.codebase)
            except service.NamespaceExists:
                self.fail("The manifest tries to create a namespace but it exists.")
