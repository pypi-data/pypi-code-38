# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/10/17 0017
__author__ = 'huohuo'
import re
import os
import urllib
#根据给定的网址来获取网页详细信息，得到的html就是网页的源代码
def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html.decode('UTF-8')

def getImg(html):
    reg = r'src="(.+?\.jpg)" pic_ext'
    imgre = re.compile(reg)
    imglist = imgre.findall(html)#表示在整个网页中过滤出所有图片的地址，放在imglist中
    x = 0
    path = u'H:\晶云公司\\1.需求文档\下载报告\晶苗\\3.新版\图片2'
   # 将图片保存到D:\\test文件夹中，如果没有test文件夹则创建
    if not os.path.isdir(path):
        os.makedirs(path)
    paths = path+'\\'      #保存在test路径下

    for imgurl in imglist:
        urllib.urlretrieve(imgurl,'{}{}.jpg'.format(paths,x))  #打开imglist中保存的图片网址，并下载图片保存在本地，format格式化字符串
        x = x + 1
    return imglist
html = getHtml("http://tieba.baidu.com/p/2460150866")#获取该网址网页详细信息，得到的html就是网页的源代码
print (getImg(html)) #从网页源代码中分析并下载保存图片
if __name__ == "__main__":
    pass
    

