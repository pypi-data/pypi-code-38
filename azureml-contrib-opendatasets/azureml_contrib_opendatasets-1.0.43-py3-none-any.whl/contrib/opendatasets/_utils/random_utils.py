# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Random related utils."""

import random
import string


def random_tag(size=5, chars=string.ascii_lowercase + string.digits):
    """Get a random tag name."""
    return ''.join(random.choice(chars) for x in range(size))
