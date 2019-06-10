# The MIT License (MIT)
#
# Copyright (c) 2013 Weizmann Institute of Science.
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from os.path import join
from tempfile import mkdtemp

import quilt
from sqlalchemy import create_engine
from whoosh import index

from .compound_cache import CompoundCache


__all__ = ("create_compound_cache_from_quilt", "DEFAULT_QUILT_PKG")


DEFAULT_QUILT_PKG = "equilibrator/cache"


def create_compound_cache_from_quilt(
    package: str = DEFAULT_QUILT_PKG, overwrite: bool = True
) -> CompoundCache:
    """
    Initialize a compound cache from a quilt data package.

    Parameters
    ----------
    package : str, optional
        The quilt data package used to initialize the compound cache.
    overwrite : bool, optional
        Re-download the quilt data if a newer version exists (default).

    """
    quilt.install(package, force=overwrite)
    location = str(mkdtemp())
    # Switch on dev mode in order to disable annoying warning regarding
    # symlinks.
    quilt._DEV_MODE = True
    quilt.export(package, location, symlinks=True)
    quilt._DEV_MODE = None
    return CompoundCache(
        create_engine(f"sqlite:///{join(location, 'compounds.sqlite')}"),
        index.open_dir(join(location, "index"), readonly=True),
    )
