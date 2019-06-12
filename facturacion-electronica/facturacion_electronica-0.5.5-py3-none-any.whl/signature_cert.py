# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util
import datetime
from OpenSSL.crypto import load_pkcs12
from OpenSSL.crypto import dump_privatekey
from OpenSSL.crypto import dump_certificate
from OpenSSL.crypto import FILETYPE_PEM
import base64

type_ = FILETYPE_PEM


class SignatureCert(object):

    def __init__(self, signature={}):
        if not signature:
            return
        util.set_from_keys(self, signature)
        if signature.get('init_signature', True):
            self._iniciar()

    @property
    def string_password(self):
        if not hasattr(self, '_string_password'):
            return False
        return self._string_password

    @string_password.setter
    def string_password(self, val):
        self._string_password = val

    @property
    def string_firma(self):
        if not hasattr(self, '_string_firma'):
            return False
        return self._string_firma

    @string_firma.setter
    def string_firma(self, val):
        self._string_firma = base64.b64decode(val)

    @property
    def priv_key(self):
        if not hasattr(self, '_priv_key'):
            return False
        return self._priv_key

    @priv_key.setter
    def priv_key(self, val):
        if type(val) is str:
            val = val.encode()
        self._priv_key = val

    @property
    def cert(self):
        if not hasattr(self, '_cert'):
            return False
        return self._cert
    
    @cert.setter
    def cert(self, val):
        self._cert = val

    @property
    def subject_serial_number(self):
        if not hasattr(self, '_subject_serial_number'):
            return False
        return self._subject_serial_number
    
    @subject_serial_number.setter
    def subject_serial_number(self, val):
        self._subject_serial_number = val

    def _iniciar(self):
        p12 = load_pkcs12(self.string_firma, self.string_password)
        cert = p12.get_certificate()
        privky = p12.get_privatekey()
        cacert = p12.get_ca_certificates()
        issuer = cert.get_issuer()
        subject = cert.get_subject()
        self.not_before = datetime.datetime.strptime(cert.get_notBefore().decode("utf-8"), '%Y%m%d%H%M%SZ')
        self.not_after = datetime.datetime.strptime(cert.get_notAfter().decode("utf-8"), '%Y%m%d%H%M%SZ')
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
        self.private_key_bits = privky.bits()
        self.private_key_check = privky.check()
        self.private_key_type = privky.type()
        self.cacert = cacert
        certificate = p12.get_certificate()
        private_key = p12.get_privatekey()
        self.priv_key = dump_privatekey(type_, private_key)
        self.cert = dump_certificate(type_, certificate)
