#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-17 15:58:22
# @Author  : Blackstone
# @to      :


import os,re,datetime


_format=[
"[^#]from\\s+(.*?)\\s+import.*?"]


_refs=[]
checked=[]





def log(*args,**kw):
	t=str(datetime.datetime.now())[:19]
	level=kw.get("level")
	if level is None:
		level="Debug"


	print("%s - Quote[%s] || -%s"%(t,level,"".join([str(x) for x in args])))


def test(path):

	check_refs(get_refs(path))

def get_refs(path):


	def get(path):

		if not os.path.exists(path):
			raise FileNotFoundError(path)

		if os.path.isdir(path):
			files=os.listdir(path)
			for file in files:
				p=os.sep.join([path,file])

				get(p)


		else:

			if(os.path.splitext(path)[1]!=".py"):return

			with open(path) as f:
				for ft in _format:

					# log("a")
					kk=re.findall(ft,f.read())

					for k in kk:

						if "." in k:
							k=k[-1]

						filename=os.path.split(path)[1].split(".")[0]
						#print("filename=>",filename)

						if filename=="__init__":
							filename=os.path.dirname(path).split(os.sep)[-1]
							#print("fix filename=>",filename)
						res=(filename,k)
						#print("res=>",res)

						#print(_refs)

						_refs.append(res)



		return _refs

	m=get(path)

	log("文件引用关系=>",_refs)

	return m
					
					


		
def check_refs(refs):
	for index in range(len(refs)):
		start=refs[index][0]
		end=refs[index][1]

		_check_ref(index,start,end)


	log("分析结束没发现可疑引用.")

def _check_ref(index,start,end):


		if start==end:
			raise RuntimeError("文件[%s]可能存在循环引用"%start)

		if index not in checked:

			next_=_get_next(end)

			if next_ is None:
				return


			log(next_)

			checked.append(index)

			res=_check_ref(index+1,start, next_[1])

		else:
			pass
		
	


def _get_next(end):

	#print("fdajfja=>",refs)

	L=[x for x in _refs if  x[0]==end]
	return None if len(L)==0 else L[0]
	


if __name__=="__main__":
	# refs=get_refs(r"C:\Users\F\git\python_daily\test\test_import")


	# check_refs(refs)

	#test(r"C:\Users\F\git\python_daily\test\test_import")

	from log import lu

	lu.getLogger().info("fda")




