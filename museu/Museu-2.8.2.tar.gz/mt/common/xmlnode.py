#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-18 16:09:34
# @Author  : Blackstone
# @to      :
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-28 14:44:03
# @Author  : Blackstone
# @to      :
from lxml import etree
from .log import lu
import re
from decimal import Decimal

log=lu.getLogger("xmlnode")

class Node():

	__NODE=None


	def __init__(self,xpath,index=0):
		self.xpath=xpath

		
		self.obj=None
		# if not self.selector.xpath(self.xpath):
		# 	self.obj=self.selector.xpath(self.xpath)[index]

		try:

			self.obj=self.selector.xpath(self.xpath)[index]


		except etree.XPathEvalError as e:
			log.info("根据(xpath=%s)没找到匹配元素"%self.xpath)

		self.child=[]

	@classmethod
	def connect(self,src):
		self.selector=etree.parse(src)
		#log.info(self.selector)


	@classmethod
	def getMatchSize(self,xpath):
		return len(self.selector.xpath(xpath))

	@staticmethod
	def fetch(xpath,index=0):
		try:
			return Node(xpath,index)
		except:
			return None


	@classmethod
	def fetch_all(cls,xpath):

		try:
			L=cls.selector.xpath(xpath)

			return [Node(xpath,o) for o in range(len(L))]

		except etree.XPathEvalError as e:
			log.info("根据(xpath=%s)没找到匹配元素"%cls.xpath)
			return []







	@staticmethod
	def getRoot():

		return Node("/UI")


	@staticmethod
	def findByPoint(point):
		
		Node.__NODE=None

		root=Node.getRoot()
		Node.__search(root,point)

		return  Node.__NODE


	@staticmethod
	def __search(startnode,point):

		#log.debug("########坐标%s=>查找node##############"%(str(point)))
		str(startnode)
		
		if startnode.isRoot():
			Node.__NODE=startnode
			# log.debug(__NODE)
			# log.debug("is root element")



		child=startnode.getChild()
		size=len(child)

		# log.debug("size="+str(size))
		# log.debug("isroot=>"+str(child[0].isRoot()))

		if size<1:
			pass

		else:

			for node in child:
				#log.debug("node=>"+str(node.getXpath()))
				#log.debug(node.isRoot())
		
				cur=Node.__NODE.getAreaSize()
				#log.debug("cur=>"+str(cur))

				if node.isLocated(point) and node.getAreaSize()<=cur:

					Node.__NODE=node
					Node.__search(node,point)



	@staticmethod
	def findXpathByPoint(t):
		node=Node.findByPoint(t)
		resouceId=node.getAttr("resource-id")
		text=node.getAttr("text")
		isListChild=node.isLocatedTOList()

		if isListChild:return "//node[@tzm=\"%s\"]"%node.getAttr("tzm")
		if text!="N":return "//node[@text=\"%s\"]"%node.getAttr("text")
		if resouceId!="N":return "//node[@resource-id=\"%s\"]"%node.getAttr("resource-id")

		xpath="//node[@tzm=\"%s\"]"%node.getAttr("tzm")
		log.warn("获得一个默认形式的xpath=>"+xpath)

		return xpath




	def getRectInfo(self,scale=1):

		pos=self.getPosition()
		x=Decimal(pos[0])/scale
		y=Decimal(pos[1])/scale
		w=Decimal(pos[2]-pos[0])/scale
		h=Decimal(pos[3]-pos[1])/scale
		#log.info(x,y,w,h)
		return (x,y,w,h)




	def isRoot(self):
		return True if self.xpath=="/UI" else False
	


	def getXpath(self):
		return self.xpath


	def getAttr(self,attrname):


		#return self.obj.get(attrname) if self.obj else "未知属性:"+attrname
		return self.obj.get(attrname)

	def getText(self):
		return self.selector.xpath(self.xpath+"/text()")


	def getChild(self):
		if  self.obj is None:
			return []

		lst=[it for it in self.obj]
		length=len(lst)
		#log.info(length)

		for i in range(length):
			index=i+1
			childpath=self.xpath+"/node[%s]"%index
			#log.info(childpath)

			self.child.append(Node(childpath))

		return self.child

	def getParent(self):
		len1=len(self.xpath.split("/"))
		len2=len(self.xpath.split("/")[len1-1])
		sx=len(self.xpath)-len2
		xpath=self.xpath[:sx-1]

		if xpath=="/UI":
			log.warn("已经是最顶层组件..")
			return None;


		return Node(xpath)


	def getCenter(self):

		p=self.getPosition()
		a=(Decimal(p[0])+Decimal(p[2]))/2
		b=(Decimal(p[1])+Decimal(p[3]))/2

		return (a,b)

	def getPosition(self):

		#log.debug("position=>%s"%(self.obj.get("ext")))

		cp=re.compile("\[(.*?),(.*?)\]\[(.*?),(.*?)\]")

		#log.info(type(self.obj.get("bounds")))
		#log.info(type(self.obj.get("bounds")))

		m=cp.match(self.obj.get("bounds"))

		x1=int(m.group(1))
		y1=int(m.group(2))
		x2=int(m.group(3))
		y2=int(m.group(4))

		return (x1,y1,x2,y2)


	def getAreaSize(self):
		if self.isRoot():return 1080*1920

		t=self.getPosition()
		
		return(t[2]-t[0])*(t[3]-t[1])

	def isLocated(self,point):

		t=self.getPosition()
		flag=point[0]>=t[0] and point[0]<=t[2] and point[1]>=t[1] and point[1]<=t[3]
		return True if flag  else False

	def isLocatedTOList(self):
		node=self
		count=5

		while count>0:
			clasz=node.getAttr("class")
			if clasz=="android.widget.ListView":return True
			node=node.getParent()
			if not node:return False

		return False


	def getProperties(self):

		struct={}
		struct["class"]="类名"
		struct["tzm"]="特征码"
		struct["index"]="同层索引"
		struct["text"]="文本内容"
		struct["resource-id"]="资源ID"
		struct["package"]="包名"
		struct["content-desc"]="描述信息"
		struct["checkable"]="能否选中"
		struct["checked"]="是否选中"
		struct["clickable"]="可点击"
		struct["enabled"]="是否可用"
		struct["focusable"]="可聚焦"
		struct["focused"]="已经聚焦"
		struct["scrollable"]="可滚动"
		struct["long-clickable"]="可长按"
		struct["password"]="是密码"
		struct["selected"]="已预选"
		struct["bounds"]="组件边界"


		return struct






def test():
	Node.connect("C:/Users/F/git/auto-provider/user-data/ui_24a1d070.xml")
	#node=Node.findByPoint((100,200))
	Node.findXpathByPoint((100,200))


if __name__=="__main__":
	test()