def inject_libpath():
    import os
    from pathlib import Path
    os.environ['PATH'] = ";".join(
        [os.environ['PATH'],
         str(Path(__file__).parent.joinpath('.libs'))])


inject_libpath()
del inject_libpath

from shioaji.shioaji import Shioaji
from shioaji.account import Account
from shioaji.backend.utils import on_quote, on_event
