# encoding: utf-8

import ssl
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from fdutil.path_tools import ensure_path_exists
from datetime import datetime, timedelta
from .config import get_file_path
from .constants import (DEFAULT_DIGEST,
                        DEFAULT_VALIDITY,
                        SSL_DATA_DIR,
                        SSLConstant)


def write_cert_file(cert,
                    filename,
                    filepath=SSL_DATA_DIR):

    """ Write the certificate to the specified file. """

    ensure_path_exists(filepath)

    pem_pth = get_file_path(fn=filename,
                            ext=SSLConstant.pem,
                            pth=filepath)

    der_pth = get_file_path(fn=filename,
                            ext=SSLConstant.der,
                            pth=filepath)

    cert_bytes = cert.public_bytes(serialization.Encoding.PEM)

    with open(pem_pth, 'wb') as cert_f:
        cert_f.write(
            cert_bytes
        )

    with open(der_pth, 'wb') as cert_f:
        cert_f.write(
            ssl.PEM_cert_to_DER_cert(cert_bytes.decode("ASCII"))
        )

    return pem_pth, der_pth


def generate_certificate(csr,
                         ca_cert,
                         ca_key,
                         filename,
                         filepath=SSL_DATA_DIR,
                         valid_from=datetime.utcnow(),
                         valid_until=DEFAULT_VALIDITY,
                         digest=DEFAULT_DIGEST,
                         extensions=None,
                         version1=False):

    """

    :param csr:         Certificate signing request object.
    :param ca_cert:     CA Certificate to be the issuer.
    :param ca_key:      CA Private Key.
    :param filename:    Filename for the key files, default=None
                        If None then do not write files.
    :param filepath:    Path to save the key files, default=SSL_DATA_DIR.
    :param valid_from:  datetime.datetime object denoting when the certificate will
                        be valid from.
    :param valid_until: Integer representing number of days after the valid_from date the
                        certificate will be valid for.
    :param digest:      Digest method to use, default is sha256.
    :param extensions:  Extensions to add to certificate, extensions should be
                        a list of cryptography.x509.SubjectAlternativeName objects.
    :param version1:    Specify whether this should be a v1 cert (True) or v3 (False),
                        default=False.
    :return:            Certificate object.
    """

    cert_builder = x509.CertificateBuilder(

    ).subject_name(
        csr.subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        valid_from
    ).not_valid_after(
        valid_from + timedelta(days=valid_until)
    )

    if extensions is not None:
        for extension in extensions:
            cert_builder = cert_builder.add_extension(extension,
                                                      critical=False)

    if version1:
        cert_builder._version = x509.Version.v1

    cert = cert_builder.sign(ca_key, digest, default_backend())

    pem_path, der_path = write_cert_file(cert=cert,
                                         filename=filename,
                                         filepath=filepath)

    return cert, pem_path, der_path
