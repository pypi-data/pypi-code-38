# encoding: utf-8

import os
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from . import (generate_key,
               generate_csr,
               generate_certificate,
               register_ssl_config)
from .constants import (DEFAULT_BITS,
                        DEFAULT_DIGEST,
                        DEFAULT_VALIDITY,
                        DEFAULT_CA_NAME,
                        DEFAULT_CA_SUBJECT_KEYS,
                        DEFAULT_PASSPHRASE,
                        SSL_DATA_DIR,
                        SSLConstant,
                        SSL_CONFIG)


def generate_ca(filename,
                filepath=SSL_DATA_DIR,
                subject_keys=DEFAULT_CA_SUBJECT_KEYS,
                bits=DEFAULT_BITS,
                passphrase=DEFAULT_PASSPHRASE,
                digest=DEFAULT_DIGEST,
                extensions=None,
                valid_from=datetime.utcnow(),
                valid_until=DEFAULT_VALIDITY,
                version1=False):

    """ Generate a self signed Certificate Authority.

    :param filename:        Filename to use for the CA files.
    :param filepath:        Path to save the CA files.
    :param subject_keys:    The subject keys to add to the request, see
                            cryptography.x509.oid.NameOID for keys,
                            default = DEFAULT_CA_SUBJECT_KEYS.
    :param bits:            Key length in bits, default = DEFAULT_BITS.
    :param passphrase:      The pass phrase to use to secure the CA private key when writing to file.
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

    ca_key, private_key_path, public_key_path = generate_key(bits=bits,
                                                             passphrase=passphrase,
                                                             filename=filename,
                                                             filepath=filepath)

    ca_csr, csr_path = generate_csr(key=ca_key,
                                    subject_keys=subject_keys,
                                    digest=digest,
                                    extensions=extensions,
                                    filename=filename,
                                    filepath=filepath)

    ca_cert, pem_path, der_path = generate_certificate(csr=ca_csr,
                                                       ca_cert=ca_csr,
                                                       ca_key=ca_key,
                                                       valid_from=valid_from,
                                                       valid_until=valid_until,
                                                       digest=digest,
                                                       extensions=extensions,
                                                       filename=filename,
                                                       filepath=filepath,
                                                       version1=version1)

    ca_filepaths = {
        SSLConstant.private_key: private_key_path,
        SSLConstant.public_key: public_key_path,
        SSLConstant.csr: csr_path,
        SSLConstant.pem: pem_path,
        SSLConstant.der: der_path
    }

    return ca_cert, ca_key, ca_filepaths


def get_default_ca(filepath=SSL_DATA_DIR):

    """ Generates / loads a default CA for the specified certificate dir

    IMPORTANT: The Default CA should only be used for test purposes!

    """

    ca_filepaths = {
        SSLConstant.private_key: os.path.join(filepath, u'{pth}.{ext}'.format(pth=DEFAULT_CA_NAME,
                                                                              ext=SSLConstant.private_key)),
        SSLConstant.public_key: os.path.join(filepath, u'{pth}.{ext}'.format(pth=DEFAULT_CA_NAME,
                                                                             ext=SSLConstant.public_key)),
        SSLConstant.csr: os.path.join(filepath, u'{pth}.{ext}'.format(pth=DEFAULT_CA_NAME,
                                                                      ext=SSLConstant.csr)),
        SSLConstant.pem: os.path.join(filepath, u'{pth}.{ext}'.format(pth=DEFAULT_CA_NAME,
                                                                      ext=SSLConstant.pem)),
        SSLConstant.der: os.path.join(filepath, u'{pth}.{ext}'.format(pth=DEFAULT_CA_NAME,
                                                                      ext=SSLConstant.der))
    }

    if os.path.exists(ca_filepaths[SSLConstant.private_key]) and os.path.exists(ca_filepaths[SSLConstant.pem]):
        print(u'LOADING DEFAULT CA')
        backend = default_backend()

        with open(ca_filepaths[SSLConstant.private_key], 'rb') as key_f:
            key = load_pem_private_key(key_f.read(), password=DEFAULT_PASSPHRASE, backend=backend)

        with open(ca_filepaths[SSLConstant.pem], 'rb') as pem_f:
            pem = x509.load_pem_x509_certificate(pem_f.read(), backend=backend)

        return pem, key, ca_filepaths

    else:
        print(u'CREATING DEFAULT CA')
        return generate_ca(filepath=filepath,
                           filename=DEFAULT_CA_NAME)


def generate_config_ca(name,
                       subject_keys=DEFAULT_CA_SUBJECT_KEYS,
                       bits=DEFAULT_BITS,
                       passphrase=DEFAULT_PASSPHRASE,
                       digest=DEFAULT_DIGEST,
                       extensions=None,
                       valid_from=datetime.utcnow(),
                       valid_until=DEFAULT_VALIDITY,
                       version1=False):

    cfg = register_ssl_config()
    path = os.path.join(cfg.data_path_unversioned,
                        SSL_DATA_DIR)

    ca_cert, ca_key, ca_filepaths = generate_ca(subject_keys=subject_keys,
                                                bits=bits,
                                                passphrase=passphrase,
                                                digest=digest,
                                                extensions=extensions,
                                                valid_from=valid_from,
                                                valid_until=valid_until,
                                                version1=version1,
                                                filename=name,
                                                filepath=path)

    cfg_key = u'{k}.{c}'.format(k=SSL_CONFIG,
                                c=name)

    cfg[cfg_key] = ca_filepaths

    return ca_cert, ca_key, ca_filepaths
