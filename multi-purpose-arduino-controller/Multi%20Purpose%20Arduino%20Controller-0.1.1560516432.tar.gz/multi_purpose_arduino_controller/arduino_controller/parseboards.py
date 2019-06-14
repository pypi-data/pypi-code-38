import sys

import glob
import importlib.util
import inspect
import os
from os.path import basename

from .basicboard.board import ArduinoBasicBoard

BOARDS = {}


def board_by_firmware(firmware):
    return BOARDS.get(firmware, None)


def parse_path_for_boards(path):
    global BOARDS
    dir_path = path

    boardsfolders = [
        p
        for p in glob.glob(dir_path + "/*")
        if os.path.isdir(p) and not p.endswith("__")
    ]
    loaded_firmwares = set()
    for boardfolder in boardsfolders:
        boardpy = os.path.join(boardfolder, "board.py")
        if os.path.exists(boardpy):
            spec = importlib.util.spec_from_file_location(
                "board." + basename(boardfolder), os.path.join(boardfolder, "board.py")
            )
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            for name, obj in inspect.getmembers(foo):
                if inspect.isclass(obj):
                    try:
                        fw = getattr(obj, "FIRMWARE")
                        if fw not in loaded_firmwares:
                            BOARDS[fw] = {
                                "firmware": fw,
                                "classcaller": obj,
                                "name": name,
                            }
                            loaded_firmwares.add(fw)
                    except:
                        pass
    print(path)
    print(BOARDS)


parse_path_for_boards(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(sys.modules[ArduinoBasicBoard.__module__].__file__)
        )
    )
)
