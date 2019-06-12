# encoding: utf-8

import os
from datetime import datetime
from . import (generate_key,
               generate_csr,
               generate_certificate,
               get_default_ca,
               register_ssl_config)
from .constants import (DEFAULT_BITS,
                        DEFAULT_DIGEST,
                        DEFAULT_VALIDITY,
                        DEFAULT_CERTIFICATE_SUBJECT_KEYS,
                        DEFAULT_EXTENSIONS,
                        DEFAULT_PASSPHRASE,
                        SSL_DATA_DIR,
                        SSL_CONFIG,
                        SSLConstant)


def generate_certificates(filename,
                          filepath=SSL_DATA_DIR,
                          ca_cert=None,
                          ca_key=None,
                          subject_keys=DEFAULT_CERTIFICATE_SUBJECT_KEYS,
                          bits=DEFAULT_BITS,
                          passphrase=DEFAULT_PASSPHRASE,
                          digest=DEFAULT_DIGEST,
                          extensions=DEFAULT_EXTENSIONS,
                          valid_from=datetime.utcnow(),
                          valid_until=DEFAULT_VALIDITY,
                          version1=False):

    """ Generate a self signed Certificate Authority.

    :param filename:        Filename to use for the CA files.
    :param filepath:        Path to save the CA files.
    :param ca_cert:         CA Certificate to be the issuer, default = None.
    :param ca_key:          CA Private Key, default = None.
                            If both ca_cert & ca_key are None then a default CA will be used.
    :param subject_keys:    The subject keys to add to the request, see
                            cryptography.x509.oid.NameOID for keys,
                            default = DEFAULT_CERTIFICATE_SUBJECT_KEYS.
    :param bits:            Key length in bits, default = DEFAULT_BITS.
    :param passphrase:      The pass phrase to use to secure the private key when writing to file.
    :param digest:          Digest method to use, digest should be a hash
                            from cryptography.hazmat.primitives.hashes, default = DEFAULT_DIGEST.
    :param extensions:      Extensions to add to certificate, extensions should be
                            a list of cryptography.x509.SubjectAlternativeName objects.
    :param valid_from:      datetime.datetime object denoting when the certificate will
                            be valid from.
    :param valid_until:     Integer representing number of days after the valid_from date the
                            certificate will be valid for.
    :param version1:        Specify whether this should be a v1 cert (True) or v3 (False),
                            default=False.
    :return:                CA Certificate & Key.
    """

    if ca_cert is None and ca_key is None:
        ca_cert, ca_key, _ = get_default_ca(filepath=filepath)

    key, private_key_path, public_key_path = generate_key(bits=bits,
                                                          passphrase=passphrase,
                                                          filename=filename,
                                                          filepath=filepath)

    csr, csr_path = generate_csr(key=key,
                                 subject_keys=subject_keys,
                                 digest=digest,
                                 extensions=extensions,
                                 filename=filename,
                                 filepath=filepath)

    cert, pem_path, der_path = generate_certificate(csr=csr,
                                                    ca_cert=ca_cert,
                                                    ca_key=ca_key,
                                                    valid_from=valid_from,
                                                    valid_until=valid_until,
                                                    digest=digest,
                                                    extensions=extensions,
                                                    filename=filename,
                                                    filepath=filepath,
                                                    version1=version1)

    cert_filepaths = {
        SSLConstant.private_key: private_key_path,
        SSLConstant.public_key: public_key_path,
        SSLConstant.csr: csr_path,
        SSLConstant.pem: pem_path,
        SSLConstant.der: der_path
    }

    return cert, key, cert_filepaths


def generate_config_certificates(name,
                                 ca_cert=None,
                                 ca_key=None,
                                 subject_keys=DEFAULT_CERTIFICATE_SUBJECT_KEYS,
                                 bits=DEFAULT_BITS,
                                 passphrase=DEFAULT_PASSPHRASE,
                                 digest=DEFAULT_DIGEST,
                                 extensions=DEFAULT_EXTENSIONS,
                                 valid_from=datetime.utcnow(),
                                 valid_until=DEFAULT_VALIDITY,
                                 version1=False):

    # TODO: Allow passing of CA config key to load CA!

    cfg = register_ssl_config()
    path = os.path.join(cfg.data_path_unversioned,
                        SSL_DATA_DIR)

    cert, key, filepaths = generate_certificates(filename=name,
                                                 filepath=path,
                                                 ca_cert=ca_cert,
                                                 ca_key=ca_key,
                                                 subject_keys=subject_keys,
                                                 bits=bits,
                                                 passphrase=passphrase,
                                                 digest=digest,
                                                 extensions=extensions,
                                                 valid_from=valid_from,
                                                 valid_until=valid_until,
                                                 version1=version1)

    cfg_key = u'{k}.{c}'.format(k=SSL_CONFIG,
                                c=name)

    cfg[cfg_key] = filepaths

    return cert, key, filepaths
