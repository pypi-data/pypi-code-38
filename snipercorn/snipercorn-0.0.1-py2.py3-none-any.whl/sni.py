"""
SNI + acme-tls/1 responder
"""

import ssl
from asyncio.sslproto import SSLProtocol  # type: ignore
from pathlib import Path
from ssl import SSLContext
from typing import Optional

from .config import Config

ACME_TLS_1 = b"acme-tls/1"

# OpenSSL has no way to get at the ALPN data
# before sni_callback and asyncio has no way to
# customize SSLProtocol. Monkey patch to capture
# raw handshake data. Would also be possible to
# construct our own factory for SSLProtocol and
# pass that into a non-ssl create_server().
_data_received = SSLProtocol.data_received


def show_data_received(self: SSLProtocol, data: bytes) -> bytes:
    if self._in_handshake and ACME_TLS_1 in data:  # type: ignore
        # leave note for sni_callback
        self._sslpipe._sslobj._probably_acme = True
    return _data_received(self, data)


SSLProtocol.data_received = show_data_received


class SSLObject(ssl.SSLObject):
    _probably_acme = False  # __init__ is not called, just SSLObject()._create


class SNIConfig(Config):
    """
    Config plus SNI (server name identification) - automatically load
    certificates from a directory tree based on requested hostname.
    """

    alpn_protocols = Config.alpn_protocols + [ACME_TLS_1.decode("ascii")]

    # a directory with the default dehydrated layout: config, domains.txt, certs subdomains...
    sni_path: Optional[str] = None

    sslobject_class = SSLObject

    @property
    def acme_dir(self):
        return Path(self.sni_path) / "alpn-certs"

    @property
    def certs_dir(self):
        return Path(self.sni_path) / "certs"

    def create_ssl_context(self) -> Optional[SSLContext]:
        context = super().create_ssl_context()
        context.sni_callback = self.sni_callback  # type: ignore
        context.sslobject_class = self.sslobject_class  # type: ignore
        return context

    @property
    def ssl_enabled(self) -> bool:
        return self.sni_path is not None

    def sni_callback(
        self, sslobject: SSLObject, hostname: str, sslcontext: SSLContext
    ) -> None:
        """
        Set sslobject.context as appropriate for hostname.
        """
        # It would be OK to cache context per hostname, keeping in mind the
        # certificates may change on disk.
        if hostname:
            sslobject.context = self.certificate_for_hostname(
                self.create_ssl_context(), hostname, sslobject._probably_acme
            )
        # TODO return error code on exception

    def certificate_for_hostname(
        self, context: SSLContext, hostname: str, acme: bool = False
    ) -> SSLContext:
        """
        Load the appropriate acme or regular certificate for servername.
        """
        basedir = Path(self.sni_path)  # type: ignore
        acme_dir = self.acme_dir
        certs_dir = self.certs_dir
        # syntax is a bit more complicated than this e.g. > certname
        with open(Path(basedir) / "domains.txt", "r") as domains:
            for line in domains:
                components = line.split()
                if hostname in components:
                    hostname = components[0]
        if acme:
            cert_path = acme_dir / (hostname + ".crt.pem")
            key_path = acme_dir / (hostname + ".key.pem")
        else:
            host_path = certs_dir / hostname
            cert_path = host_path / "fullchain.pem"
            key_path = host_path / "privkey.pem"

        try:
            context.load_cert_chain(cert_path, key_path)  # type: ignore
        except FileNotFoundError:
            print("Not Found:", cert_path, key_path)
            raise

        # ALPN will be negotiated against the new context
        return context

