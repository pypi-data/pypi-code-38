import six

if six.PY3:
    import os
    import sys

    # Unfortunately, grpc uses an incorrect relative import, which does not play well with python3
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
