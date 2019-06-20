import pytest

from .pkcs11 import PKCS11
from .settings import MOCK_PYKCS11


def pytest_configure(config):
  """Register markers, ..."""
  config.addinivalue_line('markers', 'skip_smartcard')


@pytest.fixture
def pkcs11(request):
  """Return real or mocked pkcs11 library.
    When testing real library, smart card should be inserted in local PC and
    constants in `settings.py` should be changed appropriately.
  """
  if MOCK_PYKCS11:
    return PKCS11(**getattr(request, 'param', dict()))
  else:
    return None  # real PyKCS11Lib will be instantiated - test locally with sc


@pytest.fixture(autouse=True)
def skip_for_smartcard(request, pkcs11):
  """Marker to skip test if testing with real pkcs11 libraary
  """
  if request.node.get_closest_marker('skip_smartcard'):
    if not isinstance(pkcs11, PKCS11):
      pytest.skip('Skipped while testing real smart card.')
