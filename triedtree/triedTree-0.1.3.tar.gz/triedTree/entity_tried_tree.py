# create by fanfan on 2019/5/29 0029
from triedTree.base_tried_tree import BaseTriedTree
import os
import pickle
import copy
class EntityTriedTree(BaseTriedTree):
    name = 'entity_tried_tree'

    def __init__(self, path=None):
        super(BaseTriedTree, self).__init__()
        self.trie_tree = {}
        if path != None:
            self._load_data_tree(path)

    def _load_data_tree(self, file_or_path):
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

    def _add_file_to_tree(self, filename):
        '''从文件中读取数据'''
        with  open(filename, 'r', encoding='utf-8') as fread:
            type = os.path.basename(filename).replace(".csv","")
            for line in fread:
                token_list = line.strip().split(",")
                if len(token_list) != 1:
                    word, word_alias = token_list
                    word_alias_list = word_alias.split("|")
                    token_list = []
                    token_list.append(word)
                    token_list += word_alias_list

                for word in token_list:
                    cn_chars = list(word.strip())
                    ref = self.trie_tree
                    for cn_char in cn_chars:
                        if cn_char not in ref:
                            ref[cn_char] = {}
                        ref = ref[cn_char]
                    ref['end'] = True
                    ref['type'] = type
                    if 'type_list' not in ref:
                        ref['type_list'] = []
                    if type not in ref['type_list']:
                        if type == 'sys.anyNumber':
                            ref['type_list'].append(type)
                        else:
                            ref['type_list'].insert(0, type)


    def update_type_list(self,type_list,add_type,word_list,add_word,status_list,add_status):
        '''
        跟新type_list
        :param type_list: 
        :param add_type: 
        :return: 
        '''
        if type_list and type_list[-1]== 'sys.anyNumber' and add_type == "sys.anyNumber":
            word_list[-1] += add_word
            last_status = status_list.pop()
            new_word = last_status[-1][0] + add_status[-1][0]
            new_start = last_status[-1][1]
            new_end = add_status[-1][2]
            new_type_list = []
            status_list.append([(new_word,new_start,new_end,new_type_list)])
        elif type_list and type_list[-1]== 'sys.any' and add_type == "sys.any":
            word_list[-1] += add_word
            last_status = status_list.pop()
            new_word = last_status[-1][0] + add_status[-1][0]
            new_start = last_status[-1][1]
            new_end = add_status[-1][2]
            new_type_list = []
            status_list.append([(new_word, new_start, new_end, new_type_list)])
        else:
            word_list.append(add_word)
            status_list.append(add_status)
            type_list .append(add_type)



    def update_status(self,orgin_string,type_list,word_list,status_list,tmp_search_word,patten_tried_tree):
        find_patten = False
        start_position, end_position =0,0

        while (tmp_search_word):
            item = tmp_search_word.pop()
            current_word, start_position, end_position, current_type_list = item

            if current_type_list == []:
                type_list.pop()
                word_list.pop()
            while current_type_list:
                type_ = current_type_list.pop(0)
                if patten_tried_tree.check_pattern_ok(type_list, type_,orgin_string[end_position:]):
                    new_item = (current_word, start_position, end_position, copy.deepcopy(current_type_list))
                    tmp_search_word.append(new_item)
                    self.update_type_list(type_list, type_, word_list, current_word, status_list,
                                          copy.deepcopy(tmp_search_word))
                    find_patten = True
                    break

            if find_patten:
                break


        return start_position, end_position,find_patten

    def process_with_patten(self, content,patten_tried_tree):
        cn_chars = content
        start_position,end_position = 0,0
        word_list = []
        type_list = []
        tmp_search_word = []
        status_list = []



        while len( cn_chars ) > 0:
            word_tree = self.trie_tree
            current_word = ""  # 当前词
            search_one_word_success = False
            for (index, cn_char) in enumerate(cn_chars):
                current_word  += cn_char

                if index == 0:
                    tmp_search_word.append((current_word, start_position, start_position  + 1,["sys.any"]))
                if cn_char not in word_tree:
                    break
                if 'end' in word_tree[cn_char]:
                    tmp_search_word.append((current_word, start_position,start_position + index + 1, copy.deepcopy(word_tree[cn_char]['type_list'])))
                word_tree = word_tree[cn_char]  # 继续深搜



            start_position, end_position, search_one_word_success = self.update_status(content,type_list, word_list,
                                                                                       status_list,
                                                                                       tmp_search_word,
                                                                                       patten_tried_tree)

            # 第一个字退出, 表示没有以第一个字开头的词
            if search_one_word_success == False:
                while status_list:
                    last_status_item = status_list.pop()
                    start_position, end_position, search_one_word_success = self.update_status(content,type_list, word_list,
                                                                                               status_list,
                                                                                               last_status_item,
                                                                                               patten_tried_tree)

                    #if search_one_word_success == False:
                    #    if type_list:
                    #        word_list.pop()
                    #        type_list.pop()

                        #if end_position > start_position and patten_tried_tree.check_pattern_ok(type_list, "sys.any",content[start_position+1:]):
                        #    search_one_word_success = True
                        #    end_position = start_position + 1
                        #    current_word = content[start_position:end_position]
                        #    self.update_type_list(type_list, "sys.any",word_list,current_word,status_list,[(current_word,start_position,end_position,[])])

                    if search_one_word_success:
                        break


            # 如果不是因为上述原因, 则从下一个字符开始搜索
            if search_one_word_success:
                if start_position != end_position  and end_position < len( content ):
                    start_position = end_position
                    cn_chars = content[end_position:]
                    tmp_search_word.clear()
                else:
                    break
            else:
                break


        intention = patten_tried_tree.get_intention(type_list)
        return self.output_json(intention,status_list,type_list)

    def output_json(self,intention,status_list,type_list):
        json_string = {
                            "intent":{},
                            'entities':[]
                       }
        if intention != "":
            json_string['intent']['name'] = intention[0]
            json_string['intent']['confidence'] = 1
            for status_item,type_item in zip(status_list,type_list):
                if type_item in ['sys.any','modal_words']:
                    continue
                entity = {}
                entity['value'] = status_item[-1][0]
                entity['start'] = status_item[-1][1]
                entity['end'] = status_item[-1][2]
                entity['entity'] = type_item
                json_string['entities'].append(entity)

        return json_string






