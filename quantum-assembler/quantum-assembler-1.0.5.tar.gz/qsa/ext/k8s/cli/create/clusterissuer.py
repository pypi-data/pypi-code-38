"""Create a new ``ClusterIssuer``."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument


class CreateClusterIssuerCommand(Command):
    command_name = 'clusterissuer'
    help_text = __doc__
    args = [
        Argument('environment',
            help="the environment to deploy the cluster issuer to."),
        Argument('kind', choices=['acme', 'x509'],
            help="specify the kind of cluster issuer."),
        Argument('name',
            help="a DNS-1123 compliant symbolic name for the ClusterIssuer."),
        Argument('--secret',
            help="specifies the secret holding the private key for an X.509 issuer."),
        Argument('--email',
            help="the email address used for ACME registration.")
    ]
    resources = ioc.class_property('k8s:ResourceCreateService')
    repo = ioc.class_property('k8s:Repository')
    codebase = ioc.class_property('core:CodeRepository')
    ops = ioc.class_property('deployment:Extension')

    def handle(self, quantum, args):
        if not args.secret:
            self.fail("Provide the private key with the --secret parameter.")
        issuer = self.resources.clusterissuer(args.name, args.secret,
            acme=args.kind=='acme', email=args.email)
        issuer.settitle(f"created ClusterIssuer '{args.name}'")
        issuer.setenvironments([self.ops.getenv(args.environment)])
        with self.codebase.commit(f"Create ClusterIssuer '{args.name}'", noprefix=True):
            self.repo.add(issuer)
            quantum.persist()
