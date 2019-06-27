import inspect
import os
import sys

real_path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
sys.path.append(real_path)

try:
    from config import Config as config
    import model
    import utils
except ImportError as e:
    print(e," 추가할 수 없습니다.")
    exit(1)

__all__ = [name for name, obj in locals().items()
           if not (name.startswith('_') or inspect.ismodule(obj))]