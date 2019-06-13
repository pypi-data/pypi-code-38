# -*- coding: utf-8 -*-
import re
import os
import json
import markdown
import codecs
import shutil
import sys
from distutils.sysconfig import get_python_lib

pattern = '#+\s'

heading = {
    'heading1': 0,
    'heading2': -1,
    'heading3': -1,
    'heading4': -1,
    'heading5': -1,
    'heading6': -1
}

htmlHead = u'''
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="python解析markdown快速生成html文档。md快速生成文档。">
<meta name="author" content="yuleMeng">

<title>pyMd2Doc</title>
<script src="https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js"></script>
<script src="static/js/index.js"></script>
<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
<!-- Main styles -->
<link href="static/css/index.css" rel="stylesheet">   
</head>
	<div class="banner">
	  <div class="container">欢迎使用pyMd2Doc。</div>
	</div>

    <div class="container docs-container">
      <div class="row">
        <div class="col-md-3">
          <div class="sidebar hidden-print affix" role="complementary">
            <div id="navigation">
				<ul class="nav sidenav" id="parentnode">
					<!-- <li class="active"><a href="#overview">概述</a></li>
					<li><a href="#-variables-">变量（Variables）</a></li> -->
				</ul>
		      </div>
          </div>
        </div>
		
        <div class="col-md-9" role="main">
          <header class="navbar navbar-inverse navbar-fixed-top docs-nav" role="banner">
		  <div class="container">
			 <nav class="collapse navbar-collapse bs-navbar-collapse" role="navigation">
			  <ul class="nav navbar-nav">
				
				<li class="active">
				  <span>pyMd2Doc</span>
				</li>

				<li>
				  <a href="#">欢迎使用</a>
				</li>
	
			  </ul>
			</nav>
			
		  </div>
		 </header>

		<div class="panel docs-content">
  

			<div class="docs-section">
'''

endHtml = u'''
</div>
		  </div>
      </div>
		
    </div>
  </div>

    
    <footer class="footer" role="contentinfo">
		<div class="container">
    
			<p>文档由yule meng维护</p>
		
		</div>
	</footer>
 '''

htmlTail = u'''
</body>
</html>
 '''


def formatHeading():
    heading['heading1'] = 0
    heading['heading2'] = -1
    heading['heading3'] = -1
    heading['heading4'] = -1
    heading['heading5'] = -1
    heading['heading6'] = -1


def updateHeading(current, headId):
    for i in range(1, 6):
        if len(current) == i:
            heading['heading%r' % i] = headId


def getMenu(filename):
    titles = []
    global heading
    headId = 1
    current = None
    preCurrent = '$'
    parentID = 0
    with open(filename, 'r', encoding='UTF-8') as f:
        for i in f.readlines():
            title = {}
            if not re.match(pattern, i.strip(' \t\n')):
                continue
            i = i.strip(' \t\n')
            current = i.split(' ')[0]
            # 当前标题级别比前一个小，则当前标题的父类标题是上一个的headId
            # 注释：#越多级别越小
            # 不论大多少个级别，只要父类级别大就是它的父类
            if len(current) > len(preCurrent):
                parentID = headId - 1
                # 更新当前级别父类
                updateHeading(current, parentID)
            # 当前级别比父类级别大，则去heading中寻找记录过的父类级别
            # 注释：#越少级别越大
            elif len(current) < len(preCurrent):
                length = len(current)
                # 当在文中出现一级标题的时候还原所有父类级别到初始值
                if length == 1:
                    formatHeading()
                    # 给当父类结果类赋值
                    parentID = 0
                else:
                    getVal = heading['heading%r' % length]
                    # 如果有记录过该级别的父类项
                    if getVal != -1:
                        parentID = getVal
                    # 改级别项没有记录则依次向上找父类，指导找到一级标题
                    else:
                        for j in range(length, 1, -1):
                            tempVal = heading['heading%r' % j]
                            if tempVal != -1:
                                parentID = tempVal
                                break
            titleName = i[len(current):].strip(' \t\n')
            title['titleName'] = titleName
            title['titleID'] = headId
            title['parentID'] = parentID
            titles.append(title)
            # print(headId, current, parentID)
            preCurrent = current
            headId += 1
    # print(titles)
    return titles


def writeFile(datas):
    jsObj = json.dumps(datas)
    fileObject = open('output/jsonFile.json', 'w')
    fileObject.write(jsObj)
    fileObject.close()


def addAnchorMark(titles, name):
    filename = os.path.join(os.getcwd(), "html", name + ".html")
    anchorHtml = u''
    with open(filename, 'r', encoding='UTF-8') as f:
        for i in f.readlines():
            for title in titles:
                old = '>' + title['titleName'] + '<'
                new = " class='docs-heading'><span class='anchor-target' id='a_" + str(title['titleID']) + "' ></span><a href='#a_" + str(title['titleID']) + "'  name='a_" + str(title['titleID']) + "' class='anchor glyphicon glyphicon-link' ></a>" + title['titleName'] + "<"
                old = old.replace("\r", "")
                i = i.replace(old, new)
            anchorHtml += i
    # print(anchorHtml)
    out_file = '%s.html' % (name)
    output_file = codecs.open(
        out_file, "w", encoding="utf-8", errors="xmlcharrefreplace")
    output_file.write(anchorHtml)
    output_file.close()
    return anchorHtml


def convertHtml(filename, json):
    in_file = '%s.md' % (filename)
    out_file = '%s.html' % (filename)
    input_file = codecs.open(in_file, mode="r", encoding="utf-8")
    text = input_file.read()
    html = markdown.markdown(text)
    output_file = codecs.open(
        out_file, "w", encoding="utf-8", errors="xmlcharrefreplace")

    htmlJson = u"<input style='display: none' id='jsonContent' value='" + json + "'></input>"
    output_file.write(htmlHead + html + endHtml + htmlJson + htmlTail)
    output_file.close()


def create(fileName):
    copyStaticFile()
    filePath = os.getcwd() + '/' + fileName
    mdFile = filePath + '.md'
    menu = getMenu(mdFile)
    # markdown转html（生成html）
    convertHtml(filePath, json.dumps(menu))
    # 给html加锚标记
    addAnchorMark(menu, filePath)
    print(fileName + " are create Successful!")

def copyStaticFile():
    sourceResDir = get_python_lib()+os.sep+"pymd2doc/html"
    dstResDir = os.getcwd()+"/static"
    if os.path.exists(dstResDir):
        #存在先删除'
        shutil.rmtree(dstResDir)

    #拷贝代码文件夹开始
    shutil.copytree(sourceResDir, dstResDir)



# ########################## 读String写入临时文件 ###########################
def createTempMd(strs, filename):
    with open(filename, "w", encoding='utf-8') as f:
        f.write(strs)


def createByString(content, newFile):
    filePath = os.getcwd() + '/' + newFile + ".md"
    createTempMd(content, filePath)
    create(newFile)
    deleFile(filePath)


def deleFile(filePath):
    # 如果文件存在
    if os.path.exists(filePath):
        # 删除文件
        os.remove(filePath)
    else:
        print('no such file:%s' % filePath)


if __name__ == "__main__":
    create("content")
