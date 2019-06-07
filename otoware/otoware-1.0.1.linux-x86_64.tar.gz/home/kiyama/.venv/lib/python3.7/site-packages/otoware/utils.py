from pathlib import Path
import struct

from numpy.ma import frombuffer


def get_data_file_path(file_name):
    file_path = Path(file_name)
    if file_path.is_absolute():
        return file_path.resolve()
    else:
        data_dir_path: Path = Path(__file__).parent.parent / "data"
        file_path = (data_dir_path / file_name).resolve()
        if file_path.exists():
            return file_path
        file_path = Path(__file__).parents[1] / file_name
        if file_path.exists():
            return file_path
        else:
            print(file_path)
            raise OSError("path not exist")


# 変換用関数群
def normalization(array) -> list:
    # エフェクトをかけやすいようにバイナリデータを[-1, +1]に正規化
    # ndArray -> ndArray
    # int16 の絶対値は 32767
    return frombuffer(array, dtype="int16") / 32768.0


def de_normalization(array) -> bytes:
    # 正規化前のバイナリデータに戻す(32768倍)
    new_data = [int(x * 32767.0) for x in array]
    return struct.pack("h" * len(new_data), *new_data)
