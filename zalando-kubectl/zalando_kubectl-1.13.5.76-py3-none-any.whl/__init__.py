# This is replaced during release process.
__version_suffix__ = '76'

APP_NAME = "zalando-kubectl"

KUBECTL_VERSION = 'v1.13.5'
KUBECTL_SHA256 = {
    'linux': '3b0ddcde72fd6ec30675f2d0500b3aff43a0bfd580602bb1c5c75c4072242f35',
    'darwin': 'b5980f5a719166ef414455b7f8e9462a3a81c72ef59018cdfca00438af7f3378'
}

STERN_VERSION = '1.10.0'
STERN_SHA256 = {
    'linux': 'a0335b298f6a7922c35804bffb32a68508077b2f35aaef44d9eb116f36bc7eda',
    'darwin': 'b91dbcfd3bbda69cd7a7abd80a225ce5f6bb9d6255b7db192de84e80e4e547b7'
}

APP_VERSION = KUBECTL_VERSION + "." + __version_suffix__
