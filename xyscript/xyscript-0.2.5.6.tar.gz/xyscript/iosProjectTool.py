#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,random
from xyscript.xylog import *

class IOSTool:
    def get_file_with_name(self,file_name,folder):
        for root, dirs, files in os.walk(folder):
            if file_name in files:
                root = str(root)
                dirs = str(dirs)
                print(root)
                
                return os.path.join(root, file_name)
        return None
        
    def get_file_end_count(self, file_path, old_str):
        Ropen=open(file_path,'r')#读取文件
        flagCount = 0
        for line in Ropen:
            if old_str in line:#如果.h文件中的某一行里包含old_str,则往这一行添加一下语句
                flagCount += 1
        return flagCount  
    
    # 产生一个satrtIndex到endIndex位长度的随机字符串
    def get_randomStr(self,satrtIndex,endIndex):
        numbers = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # random.choice()从列表中返回一个随机数
        final = (random.choice(numbers))
        # 从(50,100)列表中取出一个随机数
        index = random.randint(satrtIndex, endIndex)
        for i in range(index):
            final += (random.choice(numbers))
        return final

    def add_code(self, file_path, old_str, endTotalCount):
        # .h文件里属性的类型从这个数组里随机选
        file_data = ""
        Ropen=open(file_path,'r')
        flagCount = 0
        for line in Ropen:
            className = 'NSString'
            nameStr = IOSTool().get_randomStr(6,10)

            if old_str in line:
                flagCount += 1
                if flagCount==endTotalCount:
                    file_data += '\n@property(nonatomic,strong) '+className +' *'+nameStr+';\n'
                file_data += line
            else:
                file_data += line
        Ropen.close()
        Wopen=open(file_path,'w')
        Wopen.write(file_data)
        Wopen.close()

    def add_content_to_file(self,file_name):
        try:
            file = IOSTool().get_file_with_name(file_name,os.getcwd())
            if file == None:
                faillog("cannot find a file named " + file_name)
            else:
                end_count = IOSTool().get_file_end_count(file,"@end")
                IOSTool().add_code(file,"@end",end_count)
                successlog("add code to " + file + " success")
        except BaseException as error:
            faillog("add code to " + file_name + "failed:" + str(error))
        
    # TODO (m18221031340@163.com) 清理项目中没有用到的图片
    def clear_unused_picture(self):
        pass
    
    # TODO (m18221031340@163.com) 项目瘦身
    def thin_project(self):
        pass

    # TODO (m18221031340@163.com) 自动测试 Appium
    def auto_test(self):
        pass

    

if __name__ == "__main__":
    IOSTool().add_content_to_file("AppDelegate.h")
