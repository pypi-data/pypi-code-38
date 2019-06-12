# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util
import datetime
from OpenSSL.crypto import load_pkcs12
from OpenSSL.crypto import dump_privatekey
from OpenSSL.crypto import dump_certificate
from OpenSSL.crypto import FILETYPE_PEM
import base64

type_ = FILETYPE_PEM


class UserSignature(object):

    def __init__(self, signature):
        #util.set_from_keys(self, signature)
        self.dec_pass = signature['string_password']
        self.key_file = base64.b64decode(signature['string_firma'])
        self._iniciar()

    def _iniciar(self):
        p12 = load_pkcs12(self.key_file, self.dec_pass)
        cert = p12.get_certificate()
        privky = p12.get_privatekey()
        cacert = p12.get_ca_certificates()
        issuer = cert.get_issuer()
        subject = cert.get_subject()
        self.not_before = datetime.datetime.strptime(cert.get_notBefore().decode("utf-8"), '%Y%m%d%H%M%SZ')
        self.not_after = datetime.datetime.strptime(cert.get_notAfter().decode("utf-8"), '%Y%m%d%H%M%SZ')
        # self.final_date =
        self.subject_c = subject.C
        self.subject_title = subject.title
        self.subject_common_name = subject.CN
        self.subject_serial_number = subject.serialNumber
        self.subject_email_address = subject.emailAddress
        self.issuer_country = issuer.C
        self.issuer_organization = issuer.O
        self.issuer_common_name = issuer.CN
        self.issuer_serial_number = issuer.serialNumber
        self.issuer_email_address = issuer.emailAddress
        self.status = 'expired' if cert.has_expired() else 'valid'
        self.cert_serial_number = cert.get_serial_number()
        self.cert_signature_algor = cert.get_signature_algorithm()
        self.cert_version = cert.get_version()
        self.cert_hash = cert.subject_name_hash()
        # data privada
        self.private_key_bits = privky.bits()
        self.private_key_check = privky.check()
        self.private_key_type = privky.type()
        # self.cacert = cacert

        certificate = p12.get_certificate()
        private_key = p12.get_privatekey()

        self.priv_key = dump_privatekey(type_, private_key)
        self.cert = dump_certificate(type_, certificate)
