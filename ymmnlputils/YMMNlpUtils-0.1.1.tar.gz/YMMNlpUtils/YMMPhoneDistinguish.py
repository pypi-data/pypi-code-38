#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/25 10:21 AM
# @Author  : Slade
# @File    : YMMPhoneDistinguish.py

import pandas as pd
import numpy as np
import os
import jieba
import re
import warnings
from .Tools._file_load import _readbunchobj

warnings.filterwarnings("ignore")


class YMMPhoneDistinguish:
    def __init__(self, show_reason=False, user_dict=None, stop_words=None):
        '''
        :param show_reason:是否需要展示原因
        :param user_dict:用户自定义词典，默认调用自带词典
        :param stop_words:自定义停顿词
        '''
        self.show_reason = show_reason
        self._user_dict_path = os.path.dirname(os.path.abspath(__file__)) + '/Data/'
        self._model_path = os.path.dirname(os.path.abspath(__file__)) + '/Data/'
        if self.show_reason:
            self.INIT_REASON = {0: "逻辑拼接", 1: "命中敏感词", 2: "疑似电话数字", 3: "数字过长", 4: "涉及微信号码敏感"}
        if user_dict:
            self._user_dict_path = user_dict
        self._jieba_phone_identification = jieba.Tokenizer(dictionary=self._user_dict_path + "user_dict.txt")
        self.rule = re.compile("[^\u4e00-\u9fa50-9.]")
        # feature12:手机号有相对固定的起始位
        '''
        联通现有号段是：130、131、132、155、156、186、185，其中3G专属号段是：186、185。还有无线上网卡专属号段：145

        移动现有号段是：134、135、136、137、138、139、150、151、152、157、158、159、182、183、188、187

        电信现有号段是：133、153、180、181、189
        '''
        # 14开头的多为上网卡，99.99%人不会用来打电话
        self._phone_start_position_number = ('13', '15', '17', '18')
        if stop_words:
            self.stop_words = stop_words
        else:
            # 无意义词
            self.stop_words = ['你', '我', '的', '啊', '嗯', '是', '吧', '对', '了', '那个', '那', '就', '好', '到', '给', '噢', '这个',
                               '他',
                               '说', '在', '不',
                               '什么', '唉', '要', '也', '吗', '都', '现在', '一下', '这', '有', '就是', '不是', '呢', '好好', '能', '装',
                               '看',
                               '喂', '嘛', '知道',
                               '你好', '可以', '没有', '多少', '多', '那边', '去', '没', '怎么', '常州', '哪里', '跟', '呀', '把', '我们', '的话',
                               '货',
                               '地方', '明天',
                               '还', '行', '车', '不能', '问', '走', '等', '来', '给我', '这边', '再', '这样', '过去', '今天', '然后', '不知道',
                               '上',
                               '因为', '是不是',
                               '得', '不了', '叫', '哦', '不要', '无锡', '上面', '反正', '南京', '讲', '搞', '还是', '过来', '看看', '拉', '应该',
                               '东西', '它', '进去',
                               '托盘', '车子', '还有', '可能', '又', '从', '哪', '时候', '拿', '啦', '肯定', '大概', '你们', '差不多', '写', '跑',
                               '不行', '不到',
                               '位置']
        self._tfidf_model = _readbunchobj(self._model_path + 'train_data_tfidf_model.tfidf')
        self._model_0 = _readbunchobj(self._model_path + 'train_data_mnb_tri_0.nb')
        self._quantile = _readbunchobj(self._model_path + 'quantile.dat')
        self._last_model = _readbunchobj(self._model_path + 'last_model.gbm')
        self._km_model = _readbunchobj(self._model_path + 'kmeans.m')

    def _check_list(self, list_name):
        '''
        :param list_name:待检验的list
        :return: 处理完的list
        '''
        if not len(list_name):
            list_name = [0]
        return list_name

    def _union_last_features(self, is_disdigit, length_digital, digital_count, target_digital_count, disdigit_list,
                             target_digital_len_list, drop_duplicates_disdigit_list, is_sensitive_phone_number_start,
                             is_sensitive_phone_number_start_list, idx_position_list):
        '''
        :explation:disdigit = distinguish digit,判断是否为数字
        :param is_disdigit:是否含有纯数字
        :param length_digital:纯数字的长度
        :param digital_count:纯数字出现的次数
        :param target_digital_count:不可被50整除的数字出现的次数
        :param disdigit_list:出现的纯数字的list
        :param target_digital_len_list:出现的不可被50整除的数字长度的list
        :param drop_duplicates_disdigit_list:去重后的数字的list
        :param is_sensitive_phone_number_start:是否命中手机号有相对固定的起始位
        :param is_sensitive_phone_number_start_list:命中手机号有相对固定的起始位list
        :param idx_position_list:命中手机号有相对固定的起始位位置
        :return: 合并后的数据
        '''
        result_part1 = [is_disdigit, length_digital, digital_count, target_digital_count]
        result_part2 = [min(disdigit_list), max(disdigit_list), np.mean(disdigit_list), np.std(disdigit_list)]
        result_part3 = [result_part1[3] / max(result_part1[2], 1)]
        result_part4 = [min(target_digital_len_list), max(target_digital_len_list), np.mean(target_digital_len_list),
                        np.std(target_digital_len_list)]
        result_part5 = [sum(map(len, map(str, map(int, drop_duplicates_disdigit_list)))),
                        len(drop_duplicates_disdigit_list)]
        result_part6 = [result_part5[1] / max(1, result_part1[2])]
        result_part7 = [min(drop_duplicates_disdigit_list), max(drop_duplicates_disdigit_list),
                        np.mean(drop_duplicates_disdigit_list), np.std(drop_duplicates_disdigit_list)]
        result_part8 = [is_sensitive_phone_number_start, len(is_sensitive_phone_number_start_list),
                        min(idx_position_list),
                        max(idx_position_list), np.mean(idx_position_list), np.std(idx_position_list)]
        result = result_part1 + result_part2 + result_part3 + result_part4 + result_part5 + result_part6 + result_part7 + result_part8
        return result

    def _get_base_features(self, sentence_list):
        '''
        :param sentence: ['未来','历史','12839401',...]，list形式
        :return: [1,0,1...]，list形式
        '''
        is_disdigit = 0
        length_digital = 0
        digital_count = 0
        target_digital_count = 0
        # target_digital_list = []
        target_digital_len_list = []
        disdigit_list = []
        drop_duplicates_disdigit_list = []
        is_sensitive_phone_number_start_list = []
        idx_position = 0
        idx_position_list = []

        for i in sentence_list:
            # condition1:是否含有纯数字
            condition1 = i.isdigit()
            idx_position += 1
            if not condition1:
                continue
            # condition2:该句话是否已经识别出纯数字
            condition2 = not is_disdigit
            if condition1:
                if condition2:
                    is_disdigit = 1
                # 纯数字的长度
                length_digital += len(i)
                # 纯数字出现的次数
                digital_count += 1
                # 纯数字列表
                disdigit_list.append(float(i))
                # 去重纯数字列表
                drop_duplicates_disdigit_list = list(set(disdigit_list))
            # condition3：是否存在不可被50整除的数字
            condition3 = np.mod(int(i), 50)
            if condition1 and condition3:
                # 不可被50整除的数字出现的次数
                target_digital_count += 1
                # 不可被50整除的数字列表
                # target_digital_list.append(float(i))
                target_digital_len_list.append(len(str(i)))
            if condition1:
                # condition1_1：数字长度是否大大于3
                condition1_1 = len(str(i)) >= 3
                # condition1_1：数字是否在敏感号段内
                condition1_2 = i[:2] in self._phone_start_position_number
                if condition1_1 and condition1_2 and condition3:
                    is_sensitive_phone_number_start_list.append(float(i))

                idx_position_list.append(idx_position - 1)

        # 非空检验
        target_digital_len_list = self._check_list(target_digital_len_list)
        disdigit_list = self._check_list(disdigit_list)
        drop_duplicates_disdigit_list = self._check_list(drop_duplicates_disdigit_list)

        # 敏感词特征构造
        if len(is_sensitive_phone_number_start_list):
            is_sensitive_phone_number_start = 1
        else:
            is_sensitive_phone_number_start = 0
        if not len(idx_position_list):
            idx_position_list = [0]
        else:
            idx_position_list = list(map(lambda x: x / max((idx_position - 1), 1), idx_position_list))

        # 合并结果
        result = self._union_last_features(is_disdigit, length_digital, digital_count, target_digital_count,
                                           disdigit_list,
                                           target_digital_len_list, drop_duplicates_disdigit_list,
                                           is_sensitive_phone_number_start,
                                           is_sensitive_phone_number_start_list, idx_position_list)

        # 把结果转为df格式
        result = pd.DataFrame(np.array([result]),
                              columns=['isdigital', 'digital_length', 'digital_count', 'target_digital_count',
                                       'min_digital',
                                       'max_digital', 'mean_digital', 'std_digital',
                                       'target_digital_count_account_for_all',
                                       'target_min_digital', 'target_max_digital', 'target_mean_digital',
                                       'target_std_digital', 'drop_duplicates_length_digital',
                                       'drop_duplicates_digital_count', 'drop_duplicates_digital_count_account_for_all',
                                       'drop_duplicates_min_digital', 'drop_duplicates_max_digital',
                                       'drop_duplicates_mean_digital', 'drop_duplicates_std_digital',
                                       'is_sensitive_phone_number_start', 'sensitive_phone_number_start_number',
                                       'min_digital_position', 'max_digital_position', 'mean_digital_position',
                                       'std_digital_position'])
        return result

    def _reshape_data(self, features, quantile):
        '''
        :param features:原始数据，dataframe
        :param quantile:需要被压缩的变量及变量压缩值，dict形式
        :return:修正过的数据，dataframe
        '''
        for name in quantile.keys():
            features[name] = features[name].apply(lambda x: quantile[name] if x > quantile[name] else x)
        return features

    def _get_common_words(self, data):
        '''
        :param data:原始数据，list形式
        :return: 去除无意义词后，list形式
        '''
        result = []
        for i in data:
            if i not in self.stop_words:
                result.append(i)
        return result

    def predict(self, sentence, init_prob=0.92):
        '''
        :param sentence:初始文本，str形式
        :return: 概率值，float;类别，boolean
        '''
        sentence = self._jieba_phone_identification.lcut(self.rule.sub("", sentence))
        sentence = self._get_common_words(sentence)
        features = self._get_base_features(sentence_list=sentence)
        features = self._reshape_data(features, self._quantile)
        # 不建议以以下的方式去实现，可读性比较差
        # features = [quantile[name] if name in quantile.keys() else features[name] for name in features.columns]
        sentence = self._tfidf_model.transform([' '.join(sentence)])
        features['model0'] = self._model_0.predict_proba(sentence)[:, 0]
        prob = self._last_model.predict_proba(features)[:, 1]
        category = 1 if prob > float(init_prob) else 0
        if self.show_reason:
            if category:
                reason = str(self._km_model.predict(sentence.toarray())[0])
            else:
                reason = '-1'
            return prob[0], category, reason
        else:
            return prob[0], category
