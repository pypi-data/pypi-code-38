"""
NOTE: the key fixtures depend on ``_hazmat_rsa_private_key`` and
``_hazmat_rsa_private_key_2``, so these must be imported as well (even if not
used) in order for the fixtures to work.
"""

from authutils.testing.fixtures.keys import (
    _hazmat_rsa_private_key,
    _hazmat_rsa_private_key_2,
    rsa_private_key,
    rsa_private_key_2,
    rsa_public_key,
    rsa_public_key_2,
)
