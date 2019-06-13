import os
import requests
import json

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.x509.oid import NameOID
import datetime

from crypton.crypt_algorithms.asymmetric.dsa import DSA
from crypton.crypt_algorithms.asymmetric.rsa import RSA
from crypton.crypt_algorithms.asymmetric.ecdsa import ECDSA

current_file_path = os.getcwd()


class X509:

    def __init__(self, key_size=2048):
        self.key_size = key_size
        self.expiration = datetime.timedelta(1, 0, 0)
        self.builder_self_signed = x509.CertificateBuilder()
        self.builder_csr = x509.CertificateSigningRequestBuilder()

    @staticmethod
    def get_location():
        location = json.loads(requests.get('https://ipinfo.io').text)

        return location["country"], location["region"], location['city']

    def make_keys(self, algorithm):
        public_key, private_key = '', ''

        if algorithm == 'RSA':
            private_key, public_key = RSA(key_size=self.key_size).generate_key_pair()
        elif algorithm == 'DSA':
            private_key, public_key = DSA(key_size=self.key_size).generate_key_pair()
        elif algorithm == 'ECDSA':
            private_key, public_key = ECDSA(key_size=self.key_size).generate_key_pair()

        return private_key, public_key

    def build_cert(self, cert_type, algorithm, subject_name, alternative, email, org, org_unit):
        private_key, public_key = self.make_keys(algorithm)
        country, region, city = self.get_location()

        if cert_type == 'ss':
            # Subject Name and Issuer Name
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, region),
                x509.NameAttribute(NameOID.LOCALITY_NAME, city),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, org_unit),
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
            ])

            # not valid before
            now = datetime.datetime.utcnow()

            # not valid after
            one_year = datetime.datetime.utcnow() + datetime.timedelta(days=365)

            # serial number
            serial_number = x509.random_serial_number()

            certificate = self.builder_self_signed \
                .subject_name(subject) \
                .issuer_name(issuer) \
                .not_valid_before(now) \
                .not_valid_after(one_year) \
                .serial_number(serial_number) \
                .public_key(public_key) \
                .add_extension(x509.SubjectAlternativeName([x509.DNSName(alternative[0])]), critical=False) \
                .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True) \
                .sign(private_key=private_key,
                      algorithm=hashes.SHA256(),
                      backend=default_backend())

            return certificate, private_key

        if cert_type == 'csr':

            extensions = []

            for dns in alternative:  # Describe what sites we want this certificate for.
                extensions.append(x509.DNSName(dns))

            csr = self.builder_csr.subject_name(x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, region),
                x509.NameAttribute(NameOID.LOCALITY_NAME, city),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, org_unit),
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
            ])).add_extension(
                x509.SubjectAlternativeName(extensions), critical=False) \
                .sign(private_key, hashes.SHA256(), default_backend())

            return csr, private_key

    def file_x509(self, cert_type, algorithm, subject_name, alternative, email, org, org_unit, file_path=''):

        global extension

        if cert_type == 'ss':
            extension = '.crt'
        if cert_type == 'csr':
            extension = '.csr'

        cert, key = self.build_cert(cert_type=cert_type,
                                    algorithm=algorithm,
                                    subject_name=subject_name,
                                    alternative=alternative,
                                    email=email,
                                    org=org,
                                    org_unit=org_unit)

        private_key_bytes = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption()
        )

        if file_path:
            open(file_path + '/' + subject_name + extension, 'wb').write(
                cert.public_bytes(encoding=serialization.Encoding.PEM)
            )
            open(file_path + '/' + subject_name + '.key', 'w+').write(private_key_bytes.decode('utf-8'))

        else:
            open(file_path + '/' + subject_name + extension, 'wb').write(
                cert.public_bytes(encoding=serialization.Encoding.PEM)
            )
            open(file_path + '/' + subject_name + '.key', 'w+').write(private_key_bytes.decode('utf-8'))
