# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Base classes and methods that are used for unit tests."""


class FakeStream(object):
    """Fake stream object to test upload from stream. Needs to implement the
    save(filename) method.
    """
    def save(self, filename):
        """Write simple text to given file."""
        with open(filename, 'w') as f:
            f.write('This is a fake\n')
