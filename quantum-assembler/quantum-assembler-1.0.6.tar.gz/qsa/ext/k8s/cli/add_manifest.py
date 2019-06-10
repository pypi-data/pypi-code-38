"""Add a manifest to the repository."""
import os

import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.ext.k8s.repo import KubernetesRepository
from qsa.ext.k8s.repo import UnmanagedManifest


class AddManifestCommand(Command):
    base_path = 'ops/ansible/templates/k8s'
    command_name = 'import-manifest'
    codebase = ioc.class_property('core:CodeRepository')
    help_text = __doc__
    args = [
        Argument('src', help="source file to import."),
        Argument('--name',
            help="manifest name. If not provided, the filename is used."),
        Argument('-,', dest='message',
            help="message for the Ansible task."),
        ArgumentList('-e', dest='environments',
            help="the environments to import the manifest to."),
        Argument('--part-of', help="specifies the deployment this certificate "
            "is part of.")
    ]

    def handle(self, quantum, args):
        fn = os.path.basename(args.src)
        name = args.name or fn
        if not self.codebase.exists(self.base_path):
            self.codebase.mkdir(self.base_path)
        repo = KubernetesRepository(self.base_path)
        manifest = repo.get(UnmanagedManifest, name)
        manifest.setcontentfromfile(args.src)
        manifest.settaskname(f"deployed {args.message or name}")
        manifest.setunbound(not bool(args.environments))
        manifest.setenvironments(args.environments or ['global'])
        if args.part_of:
            manifest.tag(f'ansible.quantumframework.org/part-of:{args.part_of}')
        with self.codebase.commit(f"Import manifest '{fn}'", noprefix=True):
            repo.add(manifest)
            quantum.persist()
