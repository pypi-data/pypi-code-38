import sys
import pathlib
import struct

import numpy.ma


def get_data_file_path(file_name):
    file_path = pathlib.Path(file_name)
    if file_path.is_absolute():
        return file_path.resolve()
    else:
        # 相対PATHだった時.
        # venv etc.
        file_path_venv = (pathlib.Path(sys.prefix) / "data" / file_name).resolve()
        if file_path_venv.exists():
            return file_path_venv
        # develop
        file_path_dev = (pathlib.Path.cwd() / "data" / file_name).resolve()
        if file_path_dev.exists():
            print("dev:", file_path_dev)
            return file_path_dev.resolve()
        else:
            print(file_path)
            raise OSError("wav file path not exist")


# 変換用関数群
def normalization(array) -> list:
    # エフェクトをかけやすいようにバイナリデータを[-1, +1]に正規化
    # ndArray -> ndArray
    # int16 の絶対値は 32767
    return numpy.ma.frombuffer(array, dtype="int16") / 32768.0


def de_normalization(array) -> bytes:
    # 正規化前のバイナリデータに戻す(32768倍)
    new_data = [int(x * 32767.0) for x in array]
    return struct.pack("h" * len(new_data), *new_data)
