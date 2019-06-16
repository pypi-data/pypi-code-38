import ssl

from ssl import SSLContext, VerifyFlags, VerifyMode  # type: ignore
from typing import Any, AnyStr, Dict, List, Mapping, Optional, Type, Union

import hypercorn.config


class Config(hypercorn.Config):
    """
    Hypercorn's Config class tweaked to allow subclasses to override certfile loading.
    """

    def create_ssl_context(self) -> Optional[SSLContext]:
        if not self.ssl_enabled:
            return None

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.set_ciphers(self.ciphers)
        cipher_opts = 0
        for attr in ["OP_NO_SSLv2", "OP_NO_SSLv3", "OP_NO_TLSv1", "OP_NO_TLSv1_1"]:
            if hasattr(ssl, attr):  # To be future proof
                cipher_opts |= getattr(ssl, attr)
        context.options |= cipher_opts  # RFC 7540 Section 9.2: MUST be TLS >=1.2
        context.options |= (
            ssl.OP_NO_COMPRESSION
        )  # RFC 7540 Section 9.2.1: MUST disable compression
        # Not bothering with NPN
        context.set_alpn_protocols(self.alpn_protocols)

        # don't need a default certificate to begin SNI...
        # (will exclude clients who don't send a servername)
        if self.certfile is not None and self.keyfile is not None:
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        if self.ca_certs is not None:
            context.load_verify_locations(self.ca_certs)
        if self.verify_mode is not None:
            context.verify_mode = self.verify_mode
        if self.verify_flags is not None:
            context.verify_flags = self.verify_flags

        return context
