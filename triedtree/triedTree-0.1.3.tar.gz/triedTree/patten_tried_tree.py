# create by fanfan on 2019/5/29 0029
# create by fanfan on 2019/1/30 0030
from triedTree.base_tried_tree import BaseTriedTree
import os
import pickle
import copy

class PattenTriedTree(BaseTriedTree):
    name = 'patten_tried_tree'
    def __init__(self,path=None):
        self.modal_slot_name = 'modal_words'
        super(BaseTriedTree,self).__init__()
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
            intention_name = os.path.basename(filename).replace(".csv","")
            priority =3
            for line in fread:
                line  = line.strip()
                if line == "":
                    continue

                token_list = line.split(",")[0].split("@")
                sub_pattens = [token.replace("{","").replace("}","") for token in token_list if token != ""]
                self._insert_word_and_type_to_tree(sub_pattens,intention_name,priority)

    def _insert_word_and_type_to_tree(self,sub_pattens,intention,priority):
        current_root = self.trie_tree
        for token in sub_pattens:
            if token not in current_root:
                current_root[token] = {}
            current_root = current_root[token]
        current_root['end'] = True
        if 'intention_list' not in current_root:
            current_root['intention_list'] = []
        current_root['intention_list'].append(intention)



    def check_pattern_ok(self,type_list,add_type,left_words):
        '''
        在检测过程中，判断type_list是否在当前pattern_tried_tree中
        :param type_list: 
        :return: 
        '''
        root = self.trie_tree
        tmp_type_list = [type for type in type_list if type != 'modal_words']

        no_change = True
        if type_list and type_list[-1] == 'sys.anyNumber' and add_type == "sys.anyNumber":
            pass
        elif type_list and type_list[-1] == 'sys.any' and add_type == "sys.any":
            pass
        elif add_type == "modal_words":
            pass
        else:
            tmp_type_list.append(add_type)
            no_change = False


        find_pattent = True
        if not left_words:
            no_change = False

        if not no_change:
            for item in tmp_type_list:
                if item in root:
                    root = root[item]
                else:
                    find_pattent = False
            if not left_words:
                if 'end' in root:
                    find_pattent = True
                else:
                    find_pattent = False

        return find_pattent


    def get_intention(self,type_list):
        root = self.trie_tree
        itention = ""
        for item in type_list:
            if item in root:
                root = root[item]
        if 'end' in root:
            itention = root['intention_list']

        return itention

