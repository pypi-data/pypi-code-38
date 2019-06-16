#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass

PW_NUM = 0
PW_ARRAY = []

class Interaction:
    def get_user_input(self,des,password=False,pw_num=None):
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


if __name__ == "__main__":
#   print(Interaction().get_user_input("please enter password"))
  print(Interaction().get_user_input("please enter password",password=True,pw_num=2))