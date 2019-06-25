import pytest

from algernon.aws import SneakyKipper


@pytest.mark.squirrel
class TestSquirrel:
    def test_squirrel_decrypt(self):
        unencrypted = 'testing, testing, 123'
        encryption_context = {'username': 'AROA2SDLU7J62MMDYWKJB:jcubeta'}
        kipper = SneakyKipper('pagination')
        encrypted = kipper.encrypt(unencrypted, encryption_context)
        decrypted = SneakyKipper('pagination').decrypt(encrypted, encryption_context)
        assert decrypted == unencrypted
