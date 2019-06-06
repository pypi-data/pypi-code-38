"""Create Kubernetes resources."""
from qsa.lib.cli import Command
from .certificate import CreateCertificateCommand
from .clusteradmin import CreateClusterAdminCommand
from .clusterissuer import CreateClusterIssuerCommand
from .configmap import CreateConfigMapCommand
from .dmz import CreateDemilitarizedZoneCommand
from .ingress import CreateIngressCommand
from .lb import CreateLoadBalancerCommand
from .ns import CreateNamespaceCommand
from .pairednetworkpolicy import CreatePairNetworkPolicyCommand
from .pki import CreatePublicKeyInfrastructureCommand
from .serviceaccount import CreateServiceAccountCommand
from .nginx_ingress import CreateIngressNginxCommand


class CreateCommand(Command):
    command_name = 'create'
    subcommands = [
        CreateConfigMapCommand,
        CreateNamespaceCommand,
        CreateServiceAccountCommand,
        CreatePublicKeyInfrastructureCommand,
        CreateIngressNginxCommand,
        CreateDemilitarizedZoneCommand,
        CreateClusterIssuerCommand,
        CreateCertificateCommand,
        CreatePairNetworkPolicyCommand,
        CreateClusterAdminCommand,
        CreateLoadBalancerCommand,
        CreateIngressCommand,
    ]
    help_text = (
        "Specify the resource to create. For a list of valid resource names, "
        "run qsa k8s create --help"
    )
