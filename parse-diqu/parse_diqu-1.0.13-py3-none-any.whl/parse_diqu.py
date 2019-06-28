# encoding=utf-8
import json
import os
import re
from lmf.dbv2 import db_query
from bs4 import BeautifulSoup
import jieba
import collections
import time

class parseDiqu(object):

    def __init__(self):
        self.__jieba_init__()

    def __jieba_init__(self):
        json_path = os.path.join(os.path.dirname(__file__), 'xzqh_key_word.json')

        with open(json_path, 'r', encoding='utf-8') as f:
            self.xzqh_key_word = f.read()
        self.xzqh_key_word_dict_list = json.loads(self.xzqh_key_word)

        diqu = re.findall('\"word": \"([^"]+)\"', self.xzqh_key_word)
        new_diqu_list = []
        for d in diqu:
            new_diqu_list.extend(d.split(','))

        jieba.load_userdict(new_diqu_list)

    def t_page(self, page):
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

    def count_diqu(self, txt_list):
        txt2 = ''.join(txt_list)

        object_list = []
        for word in jieba.cut(txt2, cut_all=False):
            for xzqh in self.xzqh_key_word_dict_list:
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

    def parse_diqu(self, page):
        """

        :param page: html 文本
        :return: diqu_code
        """
        txt_list = self.t_page(page)
        diqu_code = self.count_diqu(txt_list)
        return diqu_code


if __name__ == '__main__':
    bt =time.time()
    p_diqu = parseDiqu()
    conp = ['postgres', 'since2015', '192.168.3.171', 'anbang', 'anhui_anqing']
    res = db_query('select page from gg_html', dbtype='postgresql', conp=conp)
    res_list = res.values.tolist()
    for t in res_list:
        p_diqu.parse_diqu(t[0])
    print(time.time()-bt)