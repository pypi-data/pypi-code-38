import ipaddress
import uuid

from dataclasses import dataclass
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


one_day = timedelta(1, 0, 0)


@dataclass
class TlsInfo:
    cacert: x509.Certificate
    cert: x509.Certificate
    key: rsa.RSAPrivateKey


@dataclass
class Cert:
    cert: x509.Certificate
    key: rsa.RSAPrivateKey


def make_tls_info() -> TlsInfo:
    cacert = make_ca_cert()
    cert = make_cert(cacert)
    return TlsInfo(cacert.cert, cert.cert, cert.key)


def make_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )


def make_ca_cert() -> Cert:
    private_key = make_key()
    public_key = private_key.public_key()
    builder = (
        x509.CertificateBuilder()
        .subject_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA")])
        )
        .issuer_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA")])
        )
        .not_valid_before(datetime.today() - one_day)
        .not_valid_after(datetime.today() + one_day)
        .serial_number(int(uuid.uuid4()))
        .public_key(public_key)
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        )
    )
    certificate = builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
        backend=default_backend()
    )
    return Cert(certificate, private_key)


def make_cert(cacert: Cert):
    private_key = make_key()

    builder = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
        )
        .add_extension(
            x509.SubjectAlternativeName([
                # Describe what sites we want this certificate for.
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv6Address("::1")),
            ]),
            critical=False,
        )
    )
    csr = builder.sign(private_key, hashes.SHA256(), default_backend())

    assert csr.is_signature_valid

    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(cacert.cert.subject)
        .not_valid_before(datetime.today() - one_day)
        .not_valid_after(datetime.today() + one_day)
        .serial_number(int(uuid.uuid4()))
        .public_key(csr.public_key())
    )
    for extension in csr.extensions:
        cert_builder = cert_builder.add_extension(
            extension.value, critical=extension.critical
        )
    certificate = cert_builder.sign(
        private_key=cacert.key, algorithm=hashes.SHA256(), backend=default_backend()
    )
    return Cert(certificate, private_key)
