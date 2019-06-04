# coding=utf-8
from __future__ import absolute_import, print_function

import os

if os.system('python -c "import tensorflow"') == 0:
    import tensorflow

    print("Tensorflow(GPU): ", tensorflow.__version__)
else:
    print("Import tensorflow-gpu error. Trying tensorflow.")
    os.system(
        "pip install tensorflow=={}".format(
            os.environ.get("TENSORFLOW_VERSION", "1.12.0")
        )
    )
    import tensorflow

    print("Tensorflow(CPU): ", tensorflow.__version__)
