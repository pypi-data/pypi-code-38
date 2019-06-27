from pytest import raises

from credential_holder.holder import (
    CredentialHolder,
    MismatchedPassphrasesException,
    RebuiltCredentialHolder,
)


class TestHolder(object):
    def test_right_passphrase_should_return_credential(self):
        passphrase = "test"
        expected_credential = "credential"

        credential_holder = CredentialHolder(passphrase, expected_credential)

        actual_credential = credential_holder.get_credential(passphrase)

        assert actual_credential == expected_credential

    def test_wrong_passphrase_should_raise_exception(self):
        passphrase = "test"
        expected_credential = "credential"

        credential_holder = CredentialHolder(passphrase, expected_credential)

        with raises(MismatchedPassphrasesException):
            credential_holder.get_credential("not test")

    def test_rebuilt_credential_holder_should_return_credential(self):
        passphrase = "test"
        expected_credential = "credential"

        credential_holder = CredentialHolder(passphrase, expected_credential)

        new_credential_holder = RebuiltCredentialHolder(
            credential_holder.iv,
            credential_holder.passphrase_hash,
            credential_holder.encrypted_credential,
        )

        actual_credential = new_credential_holder.get_credential(passphrase)

        assert actual_credential == expected_credential

    def test_rebuilt_credential_holder_should_raise_error_on_wrong_passphrase(self):
        passphrase = "test"
        expected_credential = "credential"

        credential_holder = CredentialHolder(passphrase, expected_credential)

        new_credential_holder = RebuiltCredentialHolder(
            credential_holder.iv,
            credential_holder.passphrase_hash,
            credential_holder.encrypted_credential,
        )

        with raises(MismatchedPassphrasesException):
            new_credential_holder.get_credential("not test")
