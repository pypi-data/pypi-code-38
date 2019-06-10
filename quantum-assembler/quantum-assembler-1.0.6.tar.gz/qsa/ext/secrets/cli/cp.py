"""Copies the specified secret to the specified
destination.
"""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import Enable
from .utils import print_mutation_warning


class CopySecretCommand(Command):
    command_name = 'cp'
    args = [
        Argument('src',
            help="specifies the source secret in the form of "
                 "<vault>/<namespace>/<name>"),
        Argument('dst',
            help="specifies the destination secret in the form of "
                 "<vault>/<namespace>/<name>"),
        Enable('--noprefix',
            help="do not prefix the namespace name with the "
                 "environment alias."),
        Enable('-f', '--force', dest='force',
            help="force overwriting of existing secrets. If "
                 "the destination secret exists and -f is not "
                 "supplied, nothing is done."),
        Enable('--quiet',
            help="suppress prompts.")
    ]
    vaults = ioc.class_property('secrets:VaultManager')
    deployments = ioc.class_property('deployment:Extension')
    codebase = ioc.class_property('core:CodeRepository')

    def parsepath(self, value, prefix=True):
        env, ns, name = str.split(value, '/')
        if prefix:
            ns = self.getnamespacequalname(env, ns)
        return env, ns, name

    def getsourcesecret(self, vault, namespace, name):
        return self.vaults.decrypt(vault, namespace, name)

    def getnamespacequalname(self, environment, name):
        """Return the qualified name of the namespace within
        its environment.
        """
        alias = self.deployments.getalias(environment)
        return f'ns{alias}{name}'

    def handle(self, args):
        if not args.quiet:
            print_mutation_warning()
        if args.src.count('/') != 2:
            self.fail(f"Invalid source format: {args.src}")
        if args.dst.count('/') != 2:
            self.fail(f"Invalid destination format: {args.dst}")
        src = self.getsourcesecret(
            *self.parsepath(args.src, not args.noprefix))
        if src.isnew():
            self.fail(f"Cannot resolve {args.src} to secret.")
        env, ns, name = self.parsepath(args.dst, not args.noprefix)
        dst = self.vaults.decrypt(env, ns, name)
        if not dst.isnew() and not args.force:
            self.fail(f"Destination exists in vault {env}")
        dst.update(data=src.data, type=src.type)
        with self.codebase.commit("Modified vaults", noprefix=True):
            dst.persist()
            dst.flush(self.codebase)
