import argparse
import os
from collections import Counter

import matplotlib.pyplot as plt
from wordcloud import WordCloud

from SmiToText.frequency.word import mecab_word_tags
from SmiToText.util.util import Util



def wordcloud_gen(keywords, save_path, width=800, height=800, font_path=''):
    wordcloud = WordCloud(
        font_path=font_path,
        width=width,
        height=height,
        background_color="white",
        prefer_horizontal=0.9999,  # horizontal preference
        min_font_size=10  # min font size

    )
    wordcloud = wordcloud.generate_from_frequencies(keywords)

    array = wordcloud.to_array()

    fig = plt.figure(figsize=(10, 10))
    plt.imshow(array, interpolation="bilinear")
    plt.axis("off")

    # plt.show()
    fig.savefig(save_path)


if __name__ == '__main__':
    texts = '이것 은 예문 입니다. 여러분 의 문장을 넣 으세요'
    # keywords = {'이것': 5, '예문': 3, '단어': 5, '빈도수': 3}
    default_font_path = Util().getRootPath(
        "SmiToText") + os.sep + 'data' + os.sep + 'font' + os.sep + 'NanumBarunGothic.ttf'

    parser = argparse.ArgumentParser(description="Word Cloud Generator")
    parser.add_argument('--input', type=str, required=True, default='', help='Input File')
    parser.add_argument('--output', type=str, required=True, default='', help='Word Cloud Image File')
    parser.add_argument('--font', type=str, required=False, default='', help='Word Cloud Font File')

    args = parser.parse_args()
    if not args.input:
        print("Input File is invalid!")
        exit(1)

    if not args.output:
        print("Word Cloud Image File!")
        exit(1)

    input = str(args.input)
    output = str(args.output)
    font = str(args.font)

    if not font :
        font = default_font_path

    countText = Counter()
    with open(input, encoding='utf-8', mode='r') as input_file:
        lines = input_file.readlines()
        tempCountText = Counter()
        for line in lines:
            tempCountText = mecab_word_tags(line)
            countText = countText + tempCountText

    wordcloud_gen(countText, output,font_path=font)
