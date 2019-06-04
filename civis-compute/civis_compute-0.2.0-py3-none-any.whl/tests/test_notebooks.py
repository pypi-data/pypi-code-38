from __future__ import print_function
from __future__ import division

import os
from civis.compat import TemporaryDirectory

from ..notebooks import _reformat_notebook


def test_reformat_notebook(example_notebook):
    with TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, 'script.ipynb'), 'w') as fp:
            fp.write(example_notebook)
        code = _reformat_notebook(os.path.join(tmpdir, 'script.ipynb'))

    assert code == """
# coding: utf-8

# In[ ]:


import sys

pass
    pass

""", "Notebook was not reformatted correctly!"
