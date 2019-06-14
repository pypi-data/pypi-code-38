#!/usr/bin/python
# -*- coding: UTF-8 -*-

import queue
import threading
import time

# from connection import Connection

class GetServerData:
    _instance_lock = threading.Lock()
    # 后端获取的数据
    data = queue.Queue(10)

    # 拆分后的数据
    split_data = queue.Queue(10)
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(GetServerData, "_instance"):
            with GetServerData._instance_lock:
                if not hasattr(GetServerData, "_instance"):
                    GetServerData._instance = object.__new__(cls)
        return GetServerData._instance

    def split_data_func(self):
        temp_data = None
        # 服务器返回数据
        if not self.data.empty():
            temp_data = self.data.get_nowait()
        # 返回的结果数组
        lists = [{} for i in range(10)]
        index = 0
        # 判断是否是字典类型
        if isinstance(temp_data,dict):
            # 循环map(key为slot)
            for slot in temp_data:
                slot_map = temp_data[slot]
                # 循环map(key为channel)
                for channel in slot_map:
                    index = index + 1
                    channel_map = slot_map[channel]
                    # 循环map(key为含氧去氧等)
                    for key in channel_map:
                        temp_list = channel_map[key]
                        # 循环list(分成10等分)
                        for arr_index in range(10):
                            temp = temp_list[arr_index : (arr_index + 1)]
                            if not lists[arr_index].__contains__(str(index)):
                                lists[arr_index][str(index)] = {}
                            lists[arr_index][str(index)][key] = temp
            for list_index in range(len(lists)):
                if not self.split_data.full():
                    self.split_data.put_nowait(lists[list_index])

    def get_single_time_data(self):
        # print('get')
        if not self.split_data.empty():
            temp = self.split_data.get_nowait()
            return temp
        if not self.data.empty():
            self.split_data_func()
            if not self.split_data.empty():
                return self.split_data.get_nowait()


if __name__ == '__main__':
    data = queue.Queue(10)
    for i in range(11):
        if not data.full():
            data.put_nowait(i)