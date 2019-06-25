# -*- coding: utf-8 -*-
import re
#  将文本文档尽量处理成句子类型


def pause(string_text, max_length=200):
    string_text = re.sub(' +', ' ', string_text)  # 先去除多余的空格
    string_text = string_text.strip()
    list_text = string_text.split(' ')  # 存入列表
    output_text = ''
    count_length = 0  # 记录当前句子的长度
    for word in list_text:
        if word == '':
            continue
        if len(word) > max_length:
            output_text = output_text + word + '。'
            count_length = 0
            continue
        if word[-1] == '。' or word[-1] == '！'or word[-1] == '？' \
                or word[-1] == '.' or word[-1] == '!' or word[-1] == '?':
            output_text = output_text + word
            count_length = 0
        else:
            count_length += len(word)
            if count_length <= max_length:
                output_text = output_text + word + '，'
            else:
                output_text = output_text + '。' + word + '，'
                count_length = len(word)
    output_text = output_text + '。'
    output_text = re.sub('。+', '。', output_text)
    return output_text
