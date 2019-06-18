#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import sys,os
from xyscript.xylog import faillog,warninglog

PW_NUM = 0
PW_ARRAY = []
SELECT_FILE_COUNT = 0

class Interaction:
    def get_user_input(self,des,password=False,pw_num=None):
        """
        获取用户输入
        des:      提示语，不加:
        password: 是否密文输入
        pw_num:   如果是密文，需要重复的次数
        """
        global PW_NUM,PW_ARRAY
        if pw_num == None:
            pw_num = 1
        pw_num = int(pw_num)
        
        if password == False:
            user_input = input(des + ":")
            return user_input
        else:
            pw = ""
            if PW_NUM == 0:
                pw = getpass.getpass(des + ":")
            else:
                pw = getpass.getpass(des + " again:")
            PW_ARRAY.append(pw)
            PW_NUM = PW_NUM +1
            if PW_NUM != pw_num :
                result =  self.get_user_input(des,password,pw_num)
                return result
            else:
                result_array = PW_ARRAY
                PW_NUM = 0
                PW_ARRAY = []
                if len(set(result_array)) == 1:
                    return result_array[0]
                else:
                    return None

    def select_directory(self,count=None):
        """
        选择一个文件夹
        count:允许用户取消的次数,默认是2次
        """
        global SELECT_FILE_COUNT
        if count == None:
            count = 2

        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.update()
        file_path = filedialog.askdirectory(initialdir=os.getcwd(), title="选择一个文件夹")

        if SELECT_FILE_COUNT >= int(count):
            faillog("you have give up choosing an folder " + str(count) + " times!") 
            return None

        if file_path == "":
            SELECT_FILE_COUNT = SELECT_FILE_COUNT + 1
            # print(SELECT_FILE_COUNT)
            warninglog("please choose an folder")
            result = self.select_directory(count=count)
            return(result)
        else:
            root.update()
            SELECT_FILE_COUNT = 0
            # root.mainloop()
            return file_path

if __name__ == "__main__":
#   print(Interaction().get_user_input("please enter password"))
#   print(Interaction().get_user_input("please enter password",password=True,pw_num=2))
    print(Interaction().select_directory(count=3))