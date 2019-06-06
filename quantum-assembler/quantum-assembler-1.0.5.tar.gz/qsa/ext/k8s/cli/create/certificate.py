"""Create a new X.509 certificate for use with TLS."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import Enable
from qsa.lib.cli import ArgumentList


class CreateCertificateCommand(Command):
    command_name = 'certificate'
    help_text = __doc__
    args = [
        Argument('issuer', nargs='+',
            help=(
                "specifies the CA that will issue the certificate. If the "
                "issuer is in a local scope (e.g. Issuer resource), specify "
                "it as <namespace>/<issuer name>."
            )
        ),
        Argument('namespace',
            help="the namespace in which the certificate is created."),
        Argument('name',
            help="specify the name of the certificate."),
        Argument('--common-name', nargs='+',
            help="the common name of the certificate. If the usage is for "
                "TLS web server authentication, the value provided here "
                "is also added as Subject Alternative Name (SAN). Template "
                "variables may be used here."),
        Enable('--usage-tls',
            help="indicate that the certificate is used for TLS web server "
                "authentication"),
        Argument('--part-of', help="specifies the deployment this certificate "
            "is part of."),
        Enable('--acme',
            help="enable ACME certificate issueing."),
        ArgumentList('-e', dest='environments',
            help="specifies the environments in which this certificate exists.")
    ]
    resources = ioc.class_property('k8s:ResourceCreateService')
    codebase = ioc.class_property('core:CodeRepository')
    repo = ioc.class_property('k8s:Repository')
    deployments = ioc.class_property('deployment:Extension')

    def handle(self, quantum, args):
        if not args.usage_tls:
            self.fail("Only --usage-tls is implemented.")
        if args.common_name:
            args.common_name = str.join(' ', args.common_name)
        if args.issuer:
            args.issuer = str.join(' ', args.issuer)
        msg = f"created X.509 certificate {args.name}"
        ns = self.repo.get('Namespace', args.namespace)
        with self.codebase.commit(msg[0].upper()+msg[1:], noprefix=True):
            crt = self.resources.certificate(args.issuer, ns.base_name,
                args.name, args.name, cn=args.common_name, istls=args.usage_tls,
                part_of=args.part_of, acme=args.acme)
            crt.settitle(msg)
            self.repo.add(crt)
            quantum.persist()

