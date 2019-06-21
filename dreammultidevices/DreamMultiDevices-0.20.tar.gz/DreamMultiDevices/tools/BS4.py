# -*- coding: utf-8 -*-
__author__ = "无声"
from bs4 import BeautifulSoup
import os
import re

htmlpath="D:/Python3.7/lib/site-packages/DreamMultiDevices/template/template.html"
#print(htmlpath)
html=  open(htmlpath,"r",encoding='utf-8').read()
soup = BeautifulSoup(html,features="lxml")
print (soup)






