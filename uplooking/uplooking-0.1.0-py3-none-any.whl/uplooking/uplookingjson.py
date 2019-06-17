# -*- coding: utf-8 -*-


class uplooking():

    # 基于数组语法的合并
    def join_arr(self,arr=None,key_index=None,join_index=None):
        _join_key_arr = []    # key数组
        _join_value_arr = []  # value 数据数组

        # 判断类型是否是数组(如果不是转化为数组)
        if not isinstance(join_index, list):
            if join_index is not None:
                join_index = [join_index]
            else:
                join_index = []

        # 需要合并的位置如果是元素的状况下 倒序
        join_index = sorted(join_index, reverse=True)

        # 循环 总数据集
        for i in arr:

            # 如果 合并的关键字不在数组中（构建合并的部分）
            if i[key_index] not in _join_key_arr:

                data_arr = list(i)  # 该行元组转化为数组
                join_one_arr = [] # 合并部分一维数组
                join_two_arr = [] # 合并部分二维数组

                # 倒序后取出并装填到合并构建数据第一条的尾部
                for k in join_index:
                    join_two_arr.insert(0,data_arr.pop(k)) # 把数组中要合并部分剪切并放入到合并数组

                join_one_arr.append(join_two_arr) # 该行数据合并部分以数组元素到一维数组
                data_arr.append(join_one_arr) # 一维数组装填到原有数据尾部

                _join_key_arr.append(i[key_index]) # 把key 装填到key数组(单独作为索引使用)
                _join_value_arr.append(data_arr) # 对应key数组的下标顺序 装填到数据数组


            # 如果此key的第一条数据已经被生成，把需要合并部分装填到数据数组
            else:
                data_arr = list(i)  # 该行元组转化为数组
                join_two_arr = [] # 合并部分二维数组

                # 倒序后取出并装填到合并构建数据第一条的尾部
                for k in join_index:
                    join_two_arr.insert(0, data_arr[k])  # 把数组中要合并部分剪切并放入到合并数组

                # 匹配key数组中的位置 装填到数据数组
                for index,key in enumerate(_join_key_arr):
                    if i[key_index] == key:
                        _join_value_arr[index][-1].append(join_two_arr)
                        break


        return _join_value_arr




    # 基于字典语法的合并
    def setdefault_arr(self,arr=None,key_index=None,join_index=None):

        # 判断类型是否是数组(如果不是转化为数组)
        if not isinstance(join_index, list):
            if join_index is not None:
                join_index = [join_index]
            else:
                join_index = []

        # 需要合并的位置如果是元素的状况下 倒序
        join_index = sorted(join_index, reverse=True)

        data_arr = [] # 准备合并字典的数组
        for i in arr:
            dic = {i[key_index]:i} # key合并字典
            data_arr.append(dic) # 填入数组

        key_dic = {} # 合并后的字典
        for i in data_arr:
            for k, v in i.items():
                key_dic.setdefault(k, []).append(v)  # key相同的情况下 把value以数组的形式存放


        # 遍历合并后的字典
        key_arr = []
        for key,value in key_dic.items():

            first = True # 起始开关
            for i in value:

                i = list(i) # 将元组或数组转化为数组
                join_two_arr = []  # 合并部分二维数组

                if first:
                    first = False # 关闭起始开关
                    join_one_arr = []  # 合并部分一维数组

                    # 倒序后取出并装填到合并构建数据第一条的尾部
                    for k in join_index:
                        # 把数组中要合并部分剪切并放入到合并数组
                        join_two_arr.insert(0,i.pop(k))

                    # 该行数据合并部分以数组元素到一维数组
                    join_one_arr.append(join_two_arr)

                    # 原始数据被剪切后放入数组
                    key_arr.append(i)

                    # 一维数组装填到原有数据尾部
                    key_arr[-1].append(join_one_arr)
                else:

                    # 倒序后取出并装填到合并构建数据第一条的尾部
                    for k in join_index:

                        # 把数组中要合并部分剪切并放入到合并数组
                        join_two_arr.insert(0, i[k])

                    # 一维数组装填到原有数据尾部
                    key_arr[-1][-1].append(join_two_arr)

        return key_arr














