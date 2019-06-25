import threading
from typing import Optional

from api.handler.ICacheAble import ICacheAble

holder = threading.local()

def cacheHandler() -> Optional[ICacheAble]:
    try:
        return holder.key
    except:
        return None