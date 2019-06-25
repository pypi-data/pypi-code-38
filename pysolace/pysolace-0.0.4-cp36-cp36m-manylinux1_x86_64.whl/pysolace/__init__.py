def inject_lib_path():
    import os
    from pathlib import Path
    dir_path = Path(__file__).parent
    libs_path = dir_path.joinpath('.libs')
    os.environ['PATH'] = os.environ['PATH'] + ';' + libs_path.as_posix()
    os.environ['LD_LIBRARY_PATH'] = libs_path.as_posix()


inject_lib_path()
del inject_lib_path

from pysolace import solclient