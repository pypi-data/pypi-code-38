from tqdm import tqdm as tqdm_cli

old = tqdm_cli.__init__

default_args = {
    "leave":False,
    "miniters":1,
    "dynamic_ncols":True,
    "smoothing":0.1
}
def new_init(*args, **kwargs):
    global default_args
    return old(*args, **{**default_args, **kwargs})

tqdm_cli.__init__ = new_init

from .auto_tqdm import tqdm

__all__ = ["tqdm"]