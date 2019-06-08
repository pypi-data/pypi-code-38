from pathlib import Path
import numpy as np
from otoware import convert_wav_and_array as cwa, utils


class DistortionWavAndArray(cwa.WavAndArray):
    def __init__(self, origin_path: Path, result_path: Path = None,
                 distortion_level=20):
        super(DistortionWavAndArray, self).__init__(origin_path)
        self._dist_level = distortion_level

    def bytes_data_generator(self):
        # 正規化
        self._data = utils.normalization(self._data)
        frame_per_buffer = 1024
        position = 0
        size = len(self._data)
        while position < size:
            yield utils.de_normalization(distortion(
                self._data[position:position + frame_per_buffer],
                self._dist_level))
            position += frame_per_buffer

    def update(self, distortion_level=20):
        """今回の肝
        このクラスのself._dist_levelを変更したらリアルタイムで音割れ度が変わる
        """
        self._dist_level = distortion_level


# byteもしくはbyte列に対して distortion の処理をして送る
def distortion(data, gain, level=0.7, clip=True):
    """gain乗の値をもちいてdistortion
    data: numpy.ndarray
    gain: 増幅の倍率
    level: 音量
    clip: ハードクリッピングするか(下記Qiitaか論文参照)
    """
    # https://qiita.com/stringamp/items/4b6e344ddf878f5099c7#122-%E5%AE%9F%E8%A3%85
    # 単純にgain倍増幅する時は以下
    # for n in range(length):
    # new_data = data * gain
    new_data = np.sign(data) * (1 - np.exp(-1 * gain * np.abs(data)))
    if clip:
        new_data = np.clip(new_data, -1.0, 1.0)
    # 音量を調整
    new_data *= level
    return new_data
