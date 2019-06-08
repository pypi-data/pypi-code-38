import argparse

from otoware.distortion import DistortionWavAndArray
from otoware.utils import get_data_file_path


def main():
    parser = argparse.ArgumentParser(description='このプログラムの説明（なくてもよい）')  # 2. パーサを作る

    # 3. parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('-d', '--dist_level', help='distortion level', type=int, default=1024)
    parser.add_argument('-f', '--file_name', help='wav file name', default="origin.wav")

    args = parser.parse_args()
    # 多分これと別にThreadを立ててotowari_levelを更新させればいい
    play_otowari(args.file_name, args.dist_level)


def play_otowari(file_name, distortion_level=20):
    origin_path = get_data_file_path(file_name)
    # wav_file=WavAndArray(origin_path)
    wav_file = DistortionWavAndArray(origin_path,
                                     distortion_level=distortion_level)
    wav_file.play_file()


if __name__ == '__main__':
    main()
