# encoding: utf-8

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from fdutil.path_tools import ensure_path_exists
from future.utils import iteritems
from .config import get_file_path
from .constants import (DEFAULT_DIGEST,
                        DEFAULT_CERTIFICATE_SUBJECT_KEYS,
                        SSL_DATA_DIR,
                        SSLConstant)


def write_csr_file(csr,
                   filename,
                   filepath=SSL_DATA_DIR):

    """ Write the certificate to the specified file. """

    ensure_path_exists(filepath)

    pth = get_file_path(fn=filename,
                        ext=SSLConstant.csr,
                        pth=filepath)

    with open(pth, 'wb') as csr_f:
        csr_f.write(
            csr.public_bytes(serialization.Encoding.PEM)
        )

    return pth


def generate_csr(key,
                 filename,
                 filepath=SSL_DATA_DIR,
                 subject_keys=DEFAULT_CERTIFICATE_SUBJECT_KEYS,
                 digest=DEFAULT_DIGEST,
                 extensions=None):

    """ Generate a Certificate Signing Request.

    :param key:             Private Key object.
    :param filename:        Filename for the key files.
    :param filepath:        Path to save the key files, default=SSL_DATA_DIR.
    :param subject_keys:    The subject keys to add to the request, available
                            keys can be found here: cryptography.x509.oid.NameOID,
                            default = DEFAULT_CERTIFICATE_SUBJECT_KEYS.
    :param digest:          Digest method to use, digest should be a hash
                            from cryptography.hazmat.primitives.hashes, default is sha256.
    :param extensions:      Extensions to add to certificate, extensions should be
                            a list of cryptography.x509.SubjectAlternativeName objects.
    :return:                The CSR object.
    """

    csr_builder = x509.CertificateSigningRequestBuilder()

    subject_name_attrs = []
    for subject_key, value in iteritems(subject_keys):
        subject_name_attrs.append(x509.NameAttribute(subject_key, value))

    csr_builder = csr_builder.subject_name(x509.Name(subject_name_attrs))

    # Add certificate extensions
    if extensions is not None:
        for extension in extensions:
            csr_builder = csr_builder.add_extension(extension,
                                                    critical=False)

    csr = csr_builder.sign(key, digest, default_backend())

    csr_path = write_csr_file(csr=csr,
                              filename=filename,
                              filepath=filepath)

    return csr, csr_path
