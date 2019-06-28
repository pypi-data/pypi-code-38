# encoding=utf-8
import json
import os
import re
from lmf.dbv2 import db_query
from bs4 import BeautifulSoup
import jieba
import collections





def t_page(page):
    if page is None: return []
    soup = BeautifulSoup(page, 'html.parser')
    tmp = soup.find('style')
    if tmp is not None: tmp.clear()
    tmp = soup.find('script')
    if tmp is not None: tmp.clear()
    arr = []
    for w in soup.strings:
        w = w.strip()
        if w == '': continue
        if len(w) == 1: continue
        arr.append(w)
    return arr


def count_diqu(txt_list):
    json_path = os.path.join(os.path.dirname(__file__),'xzqh_key_word.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        xzqh_key_word = f.read()
    diqu = re.findall('\"word": \"([^"]+)\"', xzqh_key_word)
    new_diqu_list = []
    for d in diqu:
        new_diqu_list.extend(d.split(','))
    txt2 = ''.join(txt_list)

    # print(jieba.cut(txt2,cut_all=False))
    jieba.load_userdict(new_diqu_list)
    object_list = []
    for word in jieba.cut(txt2, cut_all=False):
        xzqh_key_word_dict_list = json.loads(xzqh_key_word)
        for xzqh in xzqh_key_word_dict_list:
            diqu_list = xzqh['word'].split(',')
            if word in diqu_list:
                object_list.append(json.dumps({word: xzqh['code']}, ensure_ascii=False))
    word_counts = collections.Counter(object_list)
    word_counts_top = word_counts.most_common(10)
    if word_counts_top != []:
        diqu_code1 = list(json.loads(word_counts_top[0][0]).values())[0]
        return diqu_code1
    else:
        return None


def parse_diqu(page):
    """

    :param page: html 文本
    :return: diqu_code
    """
    txt_list = t_page(page)
    diqu_code = count_diqu(txt_list)
    return diqu_code


if __name__ == '__main__':
    conp = ['postgres', 'since2015', '192.168.3.171', 'anbang', 'anhui_anqing']
    res = db_query('select page from gg_html limit 10', dbtype='postgresql', conp=conp)
    res_list = res.values.tolist()
    for t in res_list:
        print(t)
        print(parse_diqu(t[0]))
