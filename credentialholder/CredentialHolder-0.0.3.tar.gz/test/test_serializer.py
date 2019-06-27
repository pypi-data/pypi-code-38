from pytest import raises

from credential_holder.holder import CredentialHolder, MismatchedPassphrasesException
from credential_holder.serializer import (
    CredentialHolderSerializer,
    ImproperSerializedFormException,
)


class TestSerializer(object):
    def test_serialize_and_deserialize(self):
        passphrase = "test"
        expected_credential = "credential"

        credential_holder = CredentialHolder(passphrase, expected_credential)

        serialized_credential_holder = CredentialHolderSerializer.serialize_credential_holder(
            credential_holder
        )

        new_credential_holder = CredentialHolderSerializer.deserialize_credential_holder(
            serialized_credential_holder
        )

        actual_credential = new_credential_holder.get_credential(passphrase)

        assert actual_credential == expected_credential

    def test_bad_serialized_string_should_raise_exception(self):
        with raises(ImproperSerializedFormException):
            CredentialHolderSerializer.deserialize_credential_holder(
                "not a real serialized string"
            )

    def test_serialize_and_deserialize_maintains_passphrase_verification(self):
        passphrase = "test"
        expected_credential = "credential"

        credential_holder = CredentialHolder(passphrase, expected_credential)

        serialized_credential_holder = CredentialHolderSerializer.serialize_credential_holder(
            credential_holder
        )

        new_credential_holder = CredentialHolderSerializer.deserialize_credential_holder(
            serialized_credential_holder
        )

        with raises(MismatchedPassphrasesException):
            new_credential_holder.get_credential("not test")
