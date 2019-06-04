# create by fanfan on 2019/1/21 0021
from triedTree.components import Component
import os
import pickle

class BaseTriedTree(Component):
    name = 'base_tried_tree'
    def __init__(self,path=None):
        super(Component,self).__init__()
        self.trie_tree = {}
        if path != None:
            self._load_data_tree(path)


    def _load_data_tree(self,file_or_path):
        total_file = []
        if not os.path.isfile(file_or_path):
            files = os.listdir(file_or_path)
            for file in files:
                real_path = os.path.join(file_or_path, file)
                if os.path.isdir(real_path):
                    pass
                total_file.append(real_path)
        else:
            total_file.append(file_or_path)

        for file in total_file:
            self._add_file_to_tree(file)



    def _add_file_to_tree(self,filename):
        '''从文件中读取数据'''
        with open(filename,'r',encoding='utf-8') as fread:
            for line in fread:
                line  = line.strip()
                if line == "":
                    continue
                token_list = line.split(" ")
                word,type = token_list
                self._insert_word_and_type_to_tree(word,type)

    def _insert_word_and_type_to_tree(self,word,type):
        current_root = self.trie_tree
        for char in list(word):
            if char not in current_root:
                current_root[char] = {}
            current_root = current_root[char]
        current_root['end'] = True
        if 'type_list' not in current_root:
            current_root['type_list'] = []
        current_root['type_list'].append(type)

    def process(self,content):
        cn_chars = content
        word_list = []
        type_list = []
        tmp_search_word = []


        while len(cn_chars) > 0:
            word_tree = self.trie_tree
            current_word = ""  # 当前词
            for (index, cn_char) in enumerate(cn_chars):
                if cn_char not in word_tree:
                    break
                current_word += cn_char
                # 词结束
                if 'end' in word_tree[cn_char]:
                    tmp_search_word.append((current_word,index, word_tree[cn_char]['type_list']))
                word_tree = word_tree[cn_char]  # 继续深搜


            # 没有找到以这个字开头的词，继续下一个字
            if len(tmp_search_word) == 0:
                cn_chars = cn_chars[1:]
            else:
                word,index,type = tmp_search_word[-1]
                word_list.append(word)
                type_list.append(type)
                cn_chars = cn_chars[index +1:]
                tmp_search_word = []

        return word_list, type_list


    def persist(self,model_dir):
        with open(model_dir,'wb') as fwrite:
            pickle.dump(self.trie_tree,fwrite)

    def restore(self, model_dir):
        with open(model_dir,'rb') as fread:
            self.trie_tree = pickle.load(fread)



if __name__ == '__main__':

    sample_data_path = '../../data/sample_tried_tree.csv'
    tree = BaseTriedTree(sample_data_path)

    sample_string = "我喜欢小米手机"
    entitys, types = tree.process(sample_string)
    assert '小米手机' in entitys[0]
    assert 'phone' in types[0]








