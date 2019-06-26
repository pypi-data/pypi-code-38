#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os

def get_os_from_file():
    # redhat , sle : /etc/redhat-release
    # centos  :
    files=["/etc/redhat-release","/etc/centos-release","/etc/issue","/etc/os-release","/etc/SuSE-release","/etc/release"]
    res_str= ""
    ubuntuflag = 0
    afile = ""
    for afile in files:
        exist =  os.path.exists(afile)
        if exist:
            f=open(afile,'r')
            while True:
                line=f.readline()
                if not line:
                    f.close()
                    break
                if afile == "/etc/redhat-release":
                    if line.find("release") != -1:
                        f.close()
                        return text_processing(line)

                if afile == "/etc/centos-release":
                    if line.find("release") != -1:
                        f.close()
                        return text_processing(line)

                if afile == "/etc/issue":
                    if line.find("Mint") != -1:
                        f.close()
                        return text_processing(line)

                if afile == "/etc/os-release":
                    if line.find("NAME") != -1 and line.find("Ubuntu") !=-1:
                        res_str = res_str + "Ubuntu "
                        ubuntu_flag = 1
                    if line.find("VERSION") != -1 and ubuntu_flag == 1:
                        tmp = line.split("\"")
                        res_str = res_str + tmp[1]
                        f.close()
                        return text_processing(res_str)
                    if line.find("NAME") != -1 and ( line.find("SLE") != -1 or line.find("SUSE") != -1):
                        ubuntu_flag =0
                    if line.find("PRETTY_NAME") != -1 and ubuntu_flag == 0:
                        f.close()
                        tmp = line.split("\"")
                        return text_processing(tmp[1])
                   
                if afile == "/etc/SuSE-release":
                    if line.find("openSUSE") != -1 or line.find("SLE")!=-1:
                        f.close()
                        return text_processing(line)

                if afile == "/etc/release":
                    if line.find('Solar'):
                        f.close()
                        return text_processing(line)

    print("The operating system can not resolved")
    exit(1)
   
        
def text_processing(input_text):
    if input_text == None or isinstance(input_text,str) == False or input_text == "":
        print("wrong input for text processing in op parser")
        exit(1)
    line = input_text
    if line.find('\n') != -1:
         line = line.replace('\n','')
    if line.find('\\n') != -1:
        line = line.replace('\\n','')
    if line.find('\\l') != -1:
        line = line.replace('\\l','')
    line = line.lstrip()
    line = line.rstrip()
    return line



if __name__=="__main__":
    print(get_os_from_file())
