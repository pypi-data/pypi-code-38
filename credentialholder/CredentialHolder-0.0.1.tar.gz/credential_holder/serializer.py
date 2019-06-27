from base64 import b64decode, b64encode

from credential_holder import holder


class CredentialHolderSerializer(object):
    @staticmethod
    def serialize_credential_holder(credential_holder):
        repr_string = "holder.RebuiltCredentialHolder(%s, %s, %s)" % (
            credential_holder.iv,
            credential_holder.passphrase_hash,
            credential_holder.encrypted_credential,
        )

        return b64encode(repr_string.encode(holder.STRING_ENCODING)).decode(
            holder.STRING_ENCODING
        )

    @staticmethod
    def deserialize_credential_holder(serialized_string):
        try:
            repr_string = b64decode(
                serialized_string.encode(holder.STRING_ENCODING)
            ).decode(holder.STRING_ENCODING)

            return eval(repr_string)
        except Exception:
            raise ImproperSerializedFormException(
                "The input string was not properly made from a CredentialHolder"
            )


class ImproperSerializedFormException(Exception):

    pass


passphrase = "test"
expected_credential = "credential"

credential_holder = holder.CredentialHolder(passphrase, expected_credential)

serialized_credential_holder = CredentialHolderSerializer.serialize_credential_holder(
    credential_holder
)

print(serialized_credential_holder)
