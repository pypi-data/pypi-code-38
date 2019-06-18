# __init__.py
# Copyright (C) 2019 Info Lab. (gnyontu39@gmail.com) and contributors
#
# 20190526 : pip install tensorflow-gpu==1.9.0 exifread piexif pillow matplotlib scikit-image IPython keras cython
import inspect
import os
import sys

__version__ = '6.1905130122'

real_path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
sys.path.append(real_path)

try:
    from Engine import Engine
    from Image import Image
    import Utils
    from Log import Log
    import Model
except ImportError as e:
    print(e," 추가할 수 없습니다.")
    exit(1)


__all__ = [name for name, obj in locals().items()
           if not (name.startswith('_') or inspect.ismodule(obj))]