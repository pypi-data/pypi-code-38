#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/4/26 9:45 AM
# @Author  : Slade
# @File    : nlp_utils.py

from pypinyin import pinyin, lazy_pinyin, Style
import re


class YMMNlpUtils(object):
    def __init__(self, strict=False):
        # '''
        # :param style: 拼音识别的风格{NORMAL:zhao,TONE:zh4ao,TONE3:zhao4,INITIALS:zh,FIRST_LETTER:z,FINALS:ao}
        # :param errors:特殊符号的处理{default:不做任何处理，原样返回，ignore : 忽略该字符，replace : 替换为去掉 \u 的 unicode 编码}
        # :param output_rule:是否允许跳特殊符号进行识别{1:拼音+数字，0:中文+数字}
        # :param strict:是否进行精准匹配
        # '''
        self.style = Style.NORMAL
        self.errors = 'ignore'
        self.rule = re.compile("[^\u4e00-\u9fa5a-z0-9]")
        self._NUMBER_MAP_RELATIONSHIP = dict(zip(map(str, list(range(11))), ['\t'] * 10))
        self._NUMBER_CHINESE_MAP_RELATIONSHIP = {'ba': '8', 'er': '2', 'jiu': '9', 'ling': '0', 'liu': '6', 'qi': '7',
                                                 'san': '3',
                                                 'si': '4', 'wu': '5', 'yi': '1'}
        self._NUMBER_CHINESE_STRICT_MAP_RELATIONSHIP = {'ba': '8', 'er': '2', 'jiu': '9', 'ling': '0', 'lin': '0',
                                                        'ning': '0', 'nin': '0', 'liu': '6', 'niu': '6', 'qi': '7',
                                                        'san': '3', 'shan': '3', 'dong': '0', 'guai': '7', 'liang': '2',
                                                        'gou': '9', 'si': '4', 'shi': '4', 'wu': '5', 'yi': '1',
                                                        'yao': '1'}
        self.output_rule = 0
        self.strict = strict
        self._last_word = ''
        self._last_filtered_idx = -1

    def init_param(self):
        '''
        参数初始化
        '''
        self._last_word = ''
        self._last_filtered_idx = -1

    def _clean_sentence(self, sentence):
        '''
        数据预处理
        '''
        return self.rule.sub("", sentence)

    def _number_filter(self, sentence):
        number_list = []
        number_idx = []
        sentence_filtered = ''
        sentence_filtered_idx = []
        cnt = 0
        for s in sentence:
            if s in self._NUMBER_MAP_RELATIONSHIP.keys():
                number_list.append(s)
                sentence_filtered += self._NUMBER_MAP_RELATIONSHIP[s]
                number_idx.append(cnt)
            else:
                sentence_filtered += s
                sentence_filtered_idx.append(cnt)
            cnt += 1
        return number_list, sentence_filtered, number_idx, sentence_filtered_idx

    def _transfer_phoneticize(self, sentence):
        return lazy_pinyin(sentence, style=self.style, errors=self.errors)

    def _number_chinese_transfer(self, pinyi_word, filtered_idx):
        if not self.strict:
            self._last_word = self._NUMBER_CHINESE_MAP_RELATIONSHIP.get(pinyi_word, pinyi_word)
            self._last_filtered_idx = filtered_idx
            return self._last_word
        else:
            # 上一个字为中文数字
            condition1 = self._last_word in self._NUMBER_CHINESE_MAP_RELATIONSHIP.values()
            # 上一个字为阿拉伯数字
            condition2 = (int(self._last_filtered_idx) + 1) != int(filtered_idx)
            if condition1 or condition2:
                self._last_word = self._NUMBER_CHINESE_STRICT_MAP_RELATIONSHIP.get(pinyi_word, pinyi_word)
            else:
                self._last_word = self._NUMBER_CHINESE_MAP_RELATIONSHIP.get(pinyi_word, pinyi_word)
            self._last_filtered_idx = filtered_idx
            return self._last_word

    def get_all_phone_number(self, sentence):
        self.init_param()
        sentence = self._clean_sentence(sentence)
        number_list, sentence_filtered, number_idx, sentence_filtered_idx = self._number_filter(sentence)
        sentence_filtered = list(
            map(self._number_chinese_transfer, self._transfer_phoneticize(sentence_filtered), sentence_filtered_idx))
        cnt = 0
        for idx in number_idx:
            number = number_list[cnt]
            sentence_filtered = sentence_filtered[:idx] + [str(number)] + sentence_filtered[idx:]
            cnt += 1
        output_sentence = ''
        if not self.output_rule:
            for pair in tuple(zip(list(sentence), sentence_filtered)):
                if pair[1] in self._NUMBER_MAP_RELATIONSHIP.keys():
                    output_sentence += pair[1]
                else:
                    output_sentence += pair[0]
        return output_sentence


if __name__ == '__main__':
    YMMNlpUtils()
