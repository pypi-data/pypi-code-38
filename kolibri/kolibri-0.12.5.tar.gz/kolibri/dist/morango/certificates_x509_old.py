from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, load_pem_private_key
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.x509.name import Name

# from mptt import models

# from .utils.uuids import UUIDModelMixin, UUIDField

CERTIFICATE_ID_NAMESPACE = uuid.UUID("db6701b3-4f22-4651-b3e9-ea60d15ba0e4")

LEARNING_EQUALITY_PEN_OID = "1.3.6.1.4.1.49607"
LEARNING_EQUALITY_MORANGO_SCOPE_OID = LEARNING_EQUALITY_PEN_OID + ".1"

scope_oid = x509.ObjectIdentifier(LEARNING_EQUALITY_MORANGO_SCOPE_OID)

scopes = [
  {
    "partitions": {
      "facility": "b",
      "kind": "userspec",
      "user": "a"
    },
    "permissions": {
      "read": True,
      "write": True
    }
  },
  {
    "partitions": {
      "facility": "b",
      "kind": "crossuser",
      "user": ""
    },
    "permissions": {
      "read": True,
      "write": False
    }
  },
  {
    "partitions": {
      "facility": "b",
      "kind": "anonuser",
      "user": ""
    },
    "permissions": {
      "read": False,
      "write": True
    }
  }
]

scopejson = unicode((json.dumps(scopes)))

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

builder = x509.CertificateSigningRequestBuilder()

builder = builder.subject_name(x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, u'{"this": "was more than you bargained for"}'),
    x509.NameAttribute(NameOID.DN_QUALIFIER, u'B'*5),
]))

builder = builder.add_extension(
    x509.BasicConstraints(ca=False, path_length=None), critical=True,
)

name = x509.DirectoryName(x509.Name([
    x509.NameAttribute(
        scope_oid,
        scopejson
    ),
]))

builder = builder.add_extension(
    x509.SubjectAlternativeName([
        x509.DirectoryName(
            x509.Name([
                x509.NameAttribute(
                    scope_oid,
                    scopejson
                ),
            ])
        )
    ]), critical=False,
)

request = builder.sign(
    private_key, hashes.SHA256(), default_backend()
)

# print request.public_bytes(Encoding.DER), request.public_bytes(Encoding.PEM)

cert = x509.load_der_x509_csr(request.public_bytes(Encoding.DER), default_backend())

def extract_morango_scopes(cert):

    try:
        
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        
        for name in ext.value.get_values_for_type(x509.GeneralName):
        
            attrs = name.get_attributes_for_oid(scope_oid)

            if attrs:

                return json.loads(attrs[0].value)

    except x509.ExtensionNotFound:

        pass

    return []

print extract_morango_scopes(cert)


def verify_signature(signed_cert, signing_cert=None):

    # if no signing certificate was specified, assume it's self-signed
    if not signing_cert:
        signing_cert = signed_cert

    # extract the hashing algorithm, signature, and public key
    hash_alg = signed_cert.signature_hash_algorithm
    signature = signed_cert.signature
    signer_pubkey = signing_cert.public_key()

    # extract the appropriate TBS ("to be signed") bytes
    if hasattr(signed_cert, "tbs_certificate_bytes"):
        tbs_bytes = signed_cert.tbs_certificate_bytes
    elif hasattr(signed_cert, "tbs_certrequest_bytes"):
        tbs_bytes = signed_cert.tbs_certrequest_bytes
    elif hasattr(signed_cert, "tbs_certlist_bytes"):
        tbs_bytes = signed_cert.tbs_certlist_bytes

    # build the appropriate signature verifier (based on the key type)
    if isinstance(signer_pubkey, rsa.RSAPublicKey):
        verifier = signer_pubkey.verifier(signature, padding.PKCS1v15(), hash_alg)
    elif isinstance(signer_pubkey, ec.EllipticCurvePublicKey):
        verifier = signer_pubkey.verifier(signature, ec.ECDSA(hash_alg))
    else:
        verifier = signer_pubkey.verifier(signature, hash_alg)

    # verify the signature 
    verifier.update(tbs_bytes)
    verifier.verify()

