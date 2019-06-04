# "fontTools" package is only used for checking the supported char range of TTF/OTF fonts

import os
from fontTools.ttLib import TTFont
from typing import Union, Iterable, Set


def find_supported_range(font_path: [str]) -> Set[str]:
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f'font path: {font_path} does not exist.')
    ranges = set()
    with TTFont(font_path, 0, ignoreDecompileErrors=True) as ttf:
        for x in ttf['cmap'].tables:
            for code in x.cmap.values():
                point = int(code.replace('uni', '\\u').replace('cid', '').lower())
                ch = chr(point)
                #try:
                #     print(point, ch)
                #except UnicodeEncodeError:  # single surrogates cannot be printed out
                #     print(point)
                ranges.add(ch)
    return ranges


if __name__ == '__main__':
    ranges = find_supported_range('.\\fonts\\NotoSansCJKtc-Regular.otf')

    print('x' in ranges)