#!/usr/bin/env python
# -*- coding: utf-8 -*-

#                                                           
# Copyright (C)2017 SenseDeal AI, Inc. All Rights Reserved  
#                                                           

"""                                                   
File: text_etl.py
Author: lzl
E-mail: zll@sensedeal.ai
Last modified: 2019/4/4
Description:                                              
"""

from lxml import etree
import re


def is_blank(text):
    """
    Determine the line is blank or not.
    If `True`, the line is blank.
    """
    if len(text.strip()) == 0:
        return True
    return False


def is_short_line(text, threshold):
    """
    Determine whether the line is shorter than threshold.
    If `True`, the line is shorter than threshold.
    """
    if len(text.strip()) <= int(threshold):
        return True
    return False


def has_end_punc(text):
    """
    Determine whether the line ends with certain punctuations.
    If `True`, the line ends with other characters.
    """
    end = text.strip()[-1]
    punc = ['：', ';', '。', '？', '！', '；', '”', '）', '']
    if end not in punc:
        return True
    return False


def remove_tails(text):
    """
    Remove the unnecessary text with certain key words.
    If `True`, the line should be removed.
    """
    keywords = ['文章来源：', '责任编辑：', '责编', '原标题：', '注：', '仅供参考', '作者：', '图/',
                '关注同花顺财经', '未经第一财经授权', '此内容为第一财经原创',
                '来源：', '文章关键词：', '记者 ', '记者：', '本文', '文/', '编辑', '校对', '本文来源：', '汇率换算微信小程序']
    for word in keywords:
        if word in text:
            return True
    return False


def remove_general(text):
    """
    Remove the unnecessary text in disclosure.
    If `True`, the line should be removed.
    """
    keywords = ['证券简称', '公告编号', '虚假记载', '重大遗漏', '【活动报名】', '图片来源：',
                '免责声明', '仅代表', '如有侵权', '采编', '证券之星', '查看更多', '未经许可，请勿转载', '扫一扫', '打开微信']
    for word in keywords:
        if word in text:
            return True
    return False


def remove_handler(text):
    lines = ['责任编辑：', '返回搜狐，查看更多', '网易科技讯', '关注同花顺财经（ths518），获取更多机会']
    for line in lines:
        text = text.replace(line, '')
    if '图片来源：' in text:
        text = text.split('图片来源：')[0]
    return text


def remove_src(text):
    """
    Remove the news source from the text, only context returned.
    """
    text = str(text).strip()
    keywords = ['讯：', '讯:', '讯 ', '讯，', '消息 ', '消息:', '消息：', '报道：', '报道:', '报道 ', '消息，', '日电 ']
    for word in keywords:
        if text.find(word) != -1:
            index = text.index(word)
            text = text[index + len(word):]
            break
    idx = -1
    if text.startswith('('):
        idx = text.index(')')
    elif text.startswith('（'):
        idx = text.index('）')
    text = text[idx + 1:]

    idx = -1
    if '讯(' in text:
        idx = text.index(')')
    elif '讯（' in text:
        idx = text.index('）')
    text = text[idx + 1:]
    return text.strip()


# 处理两种格式的数据
def get_text(html):
    try:
        if '<p>' in html:
            response = etree.HTML(html)
            p_node_list = response.xpath("//p | //span")
            if len(p_node_list) <= 1:
                return re.sub('<.*?>', '', html)
            text = ''
            for p_node in p_node_list:
                # 将此段落标签下所有的文本合并成一段话
                line = ''.join([text.replace('\t', '').strip() for text in p_node.xpath("string(.)").split('\n')])
                text += line
                if line and line[-1] not in ['，', ',']:
                    text += '\n'
            return re.sub('<.*?>', '', text)
    except Exception as ex:
        pass
    return re.sub('<.*?>', '', html)


# 文本处理
def handle_text(context, threshold=3):
    context = get_text(context)
    context_list = context.split('\n')
    final_list = []
    try:
        for i in range(len(context_list)):
            if is_blank(context_list[i]):
                continue
            if is_short_line(context_list[i], threshold):
                continue
            if has_end_punc(context_list[i]):
                continue
            if remove_general(context_list[i]):
                continue
            if i >= len(context_list) - 4 and remove_tails(context_list[i]):
                continue
            if i == 0:
                context_list[i] = remove_src(context_list[i])
            context_list[i] = remove_handler(context_list[i])

            final_list.append(context_list[i].strip())

        if not final_list:
            return remove_handler(context)
        return '\n'.join(final_list)

    except Exception as ex:
        return context
