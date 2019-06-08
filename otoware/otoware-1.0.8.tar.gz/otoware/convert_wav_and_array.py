import wave
import pyaudio
from pathlib import Path


class WavAndArray:
    def __init__(self, origin_path: Path, result_path: Path = None):
        self._path: Path = origin_path
        self._result_path = result_path
        # 元のWavファイルから取得した音楽データ情報
        self._wav_info = self.get_wave_info()
        # ndarray化した音楽データ
        self._data = self.wav_to_ndarray()
        print(self._wav_info)

    # 初期化関数群
    def get_wave_info(self):
        """WAVEファイルの情報を取得"""
        with self._path.open("rb") as f, wave.open(f) as wf:
            return {'channel': wf.getnchannels(), 'width': wf.getsampwidth(),
                    'frame_rate': wf.getframerate(), 'frames': wf.getnframes(),
                    'params': wf.getparams(),
                    "long": float(wf.getnframes() / wf.getframerate())
                    }

    def wav_to_ndarray(self):
        with self._path.open("rb") as f, wave.open(f) as wf:
            return wf.readframes(self._wav_info['frames'])

    # 再生用関数群
    # byte列を(本来のwavのデータの情報を元に再生)
    def play_file(self):
        p = pyaudio.PyAudio()
        # Streamを生成(3)
        stream = p.open(
            format=p.get_format_from_width(self._wav_info['width']),
            channels=self._wav_info['channel'],
            rate=self._wav_info['frame_rate'],
            output=True)
        for byte_data in self.bytes_data_generator():
            stream.write(byte_data)
        stream.close()
        p.terminate()

    # byte列の末端になるまで1フレーム毎にデータを出力
    def bytes_data_generator(self):
        frame_per_buffer = 1024
        position = 0
        size = len(self._data)
        while position < size:
            yield self._data[position:position + frame_per_buffer]
            position += frame_per_buffer


# """保存用関数群"""
#
#
# array をwav に変換して保存
# def save_file(bit_array, origin_path: Path, result_path: Path):
#     音声を保存
#     wav_info = get_wave_info(origin_path)
#     frame_rate = wav_info['frame_rate']
#     channel = wav_info['channel']
#     ndarray_to_wav(bit_array, channel=channel, rate=frame_rate,
#                    path=result_path)
#
#
# def ndarray_to_wav(data: bytes, channel: int, rate: int, path: Path):
#     """波形データをWAVEファイルへ出力"""
#     with path.open("wb") as f, wave.open(f, "w") as wf:
#         wf.setnchannels(channel)
#         16bit // 2 で サンプルサイズは2(らしい)
# wf.setsampwidth(2)
# wf.setframerate(rate)
# wf.writeframes(data)
# print("data completely saved")
# print(get_wave_info(path=path))
