import base64
import json
import uuid
import mptt
import mptt.models

from django.db import models

from .utils.uuids import UUIDModelMixin

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from .crypto import Key
        

class RSAKeyBaseField(models.TextField):

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 1000
        super(RSAKeyBaseField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RSAKeyBaseField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs


class PublicKeyField(RSAKeyBaseField):

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return None
        return Key(public_key_string=value)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, Key):
            return value
        return Key(public_key_string=value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return value.get_public_key_string()


class PrivateKeyField(RSAKeyBaseField):

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return None
        return Key(private_key_string=value)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, Key):
            return value
        return Key(private_key_string=value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return value.get_private_key_string()


# class PrivateKey(models.Model):

#     private_key_pem = models.TextField()

#     @classmethod
#     def generate_new_key(cls):
#         key = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=2048,
#             backend=default_backend(),
#         )
#         pem = key.private_bytes(
#             encoding=serialization.Encoding.PEM,
#             format=serialization.PrivateFormat.PKCS8,
#             encryption_algorithm=serialization.NoEncryption(),
#         )
#         return cls.objects.create(private_key_pem=pem)

#     def _get_private_key_object(self):
#         if not hasattr(self, "_private_key"):
#             self._private_key = serialization.load_pem_private_key(
#                 data=self.private_key_pem,
#                 password=None,
#                 backend=default_backend(),
#             )
#         return self._private_key

#     def _get_public_key_object(self):
#         if not hasattr(self, "_public_key"):
#             self._public_key = self._get_private_key_object().public_key()
#         return self._public_key

#     def get_public_key_pem(self):
#         return self._get_public_key_object().public_bytes(
#             encoding=serialization.Encoding.PEM,
#             format=serialization.PublicFormat.PKCS1,
#         )

#     def sign(self, data):
#         return self._get_private_key_object().sign(data, padding.PKCS1v15(), hashes.SHA256())

#     def decrypt(self, ciphertext):
#         return self._get_private_key_object().decrypt(ciphertext, padding.PKCS1v15())

#     def encrypt(self, data):
#         return self._get_public_key_object().encrypt(data, padding.PKCS1v15())

#     def verify(self, value, signature):

#         pub_key = self._get_public_key_object()

#         verifier = pub_key.verifier(signature, padding.PKCS1v15(), hashes.SHA256())
        
#         verifier.update(value)
#         try:
#             verifier.verify()
#             return True
#         except InvalidSignature:
#             return False


class Certificate(mptt.models.MPTTModel, UUIDModelMixin):
    
    # the Morango profile with which this certificate is associated
    profile = models.CharField(max_length=20)

    # scope of this certificate, and version of the scope, along with associated params
    scope_definition = models.ForeignKey("ScopeDefinition")
    scope_version = models.IntegerField()
    scope_params = models.TextField()  # JSON dict of values to insert into scope definitions

    # track the certificate's public key so we can verify its certificates
    public_key = PublicKeyField()
    
    # the JSON-serialized copy of all the fields above
    serialized = models.TextField()

    # signature from the private key of the parent certificate, of the "serialized" field text
    signature = models.TextField()

    # when we own a certificate, we'll have the private key for it (otherwise not)
    private_key = PrivateKeyField(blank=True, null=True)

    def calculate_uuid(self):
        assert self.serialized, "Certificate must be generated before it can be saved!"
        return uuid.uuid5(CERTIFICATE_ID_NAMESPACE, self.serialized)

    def _get_public_key_object(self):
        if not hasattr(self, "_public_key"):
            self._public_key = serialization.load_pem_public_key(
                data=self.public_key_pem,
                password=None,
                backend=default_backend(),
            )
        return self._public_key

    def verify(self, value, signature):

        pub_key = self._get_public_key_object()

        verifier = pub_key.verifier(signature, padding.PKCS1v15(), hashes.SHA256())
        
        verifier.update(value)

        try:
            verifier.verify()
            return True
        except rsa.InvalidSignature:
            return False

    def has_subset_scope_of(self, othercert):
        own_scope = self.scope_definition.get_scope(self.scope_params)
        other_scope = othercert.scope_definition.get_scope(othercert.scope_params)
        return own_scope.is_subset_of(other_scope)


class ScopeDefinition(models.Model):
    
    # the Morango profile with which this scope is associated
    profile = models.CharField(max_length=20)

    # version number is incremented whenever scope definition is updated
    version = models.IntegerField()

    # the identifier used to specify this scope within a certificate
    scope_id = models.CharField(primary_key=True, max_length=20)
    
    # human-readable description
    # (can include string template refs to scope params e.g. "Allows syncing data for user ${username}")
    description = models.TextField()
    
    # scope definition templates, in the form of a newline-delimited list of colon-delimited partition strings
    # (can include string template refs to scope params e.g. "122211:singleuser:${useruuid}")
    read_scope_def = models.TextField()
    write_scope_def = models.TextField()
    read_write_scope_def = models.TextField()
    
    # the JSON-serialized copy of all the fields above
    serialized = models.TextField()

    # signature from the private key of a trusted private key, of the "serialized" field text
    signature = models.TextField()
    key = models.ForeignKey("TrustedKey")

    def get_scope(self, params):
        return Scope(definition=self, params=params)


class ScopeIsNotSubset(Exception):
    pass

class Scope(object):

    def __init__(self, definition, params):
        # inflate the scope definition by filling in the template values from the params
        rw_scope = self._fill_in_scope_def(definition.read_scope_def, params)
        self.read_scope = rw_scope + self._fill_in_scope_def(definition.read_scope_def, params)
        self.write_scope = rw_scope + self._fill_in_scope_def(definition.write_scope_def, params)

    def _fill_in_scope_def(self, scope_def, params):
        return tuple(string.Template(scope_def).safe_substitute(params).split())

    def _verify_subset_for_field(self, scope, fieldname):
        s1 = getattr(self, fieldname)
        s2 = getattr(scope, fieldname)
        for partition in s1:
            if not s1.startswith(s2):
                raise ScopeIsNotSubset(
                    "No partition prefix found for {partition} in {scope} ({fieldname})!".format(
                        partition=partition,
                        scope=s2,
                        fieldname=fieldname,
                    )
                )

    def verify_subset_of(self, scope):
        self._verify_subset_for_field(scope, "read_scope")
        self._verify_subset_for_field(scope, "write_scope")

    def is_subset_of(self, scope):
        try:
            self.verify_subset_of(scope)
        except ScopeIsNotSubset:
            return False
        return True


class TrustedKey(UUIDModelMixin):
    
    uuid_input_fields = "public_key"

    public_key = models.TextField()
    notes = models.TextField(blank=True)

    revoked = models.BooleanField(default=False)


{
    "name": "facility",
    "type": "uuid",
    "subpartition": {
        "name": "userkind",
        "type": "constant",
        "values": [
            {
                "value": "specific",
                "subpartition": {
                    "name": "user",
                    "type": "uuid"
                }
            },
            {
                "value": "cross"
            },
            {
                "value": "anon"
            },
        ]
    }
}

class Partition(object):

    name = None

    def __init__(self, name, *args, **kwargs):
        self.name = name
    

class ConstantPartition(Partition):

    values = None

    def __init__(self, *args, **kwargs):
        super(ConstantPartition, self).__init__(*args, **kwargs)
        self.values = {}

    def add_value(self, value):
        assert isinstance(value, ConstantPartitionValue)
        self.values[val.value] = value

class ConstantPartitionValue(object):

    value = None

    def __init__(self, value, subpartition):
        assert isinstance(value, str)
        assert isinstance(subpartition, Partition)
        self.value = value
        self.subpartition = subpartition

class UUIDPartition(Partition):

    def __init__(self, subpartition):
        assert isinstance(value, str)
        assert isinstance(subpartition, Partition)
        self.value = value
        self.subpartition = subpartition


# TODO:
# - Set and validate issuing certificate subject stuff: https://github.com/pyca/cryptography/pull/2460/files#diff-0e16667d55ca541078a5f627ae729bbeR40
# - Correct for mismatched clocks in Fernet encryption