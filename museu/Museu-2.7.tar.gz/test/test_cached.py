#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-05-28 08:48:51
# @Author  : Blackstone
# @to      :

import time
from types import MethodType,FunctionType

class cached(object):

	_result={}
	_dispatch={}

	def __init__(self,args):
		#print("args=>",args)
		self.args=args
		# print("args0=>",self.args)


	def __call__(self,*args,**kw):
		#print("self=>",self)
		# print("args1=>",args)
		# print("kw1=>",kw)


		try:
			what=args[0]
		except:
			pass

		def get_sign(*str_):
			out=""
			for _ in str_:
				out+=str(_)+'_'

			import uuid,warnings
			if len(out)>1000000000:
				warnings.warn("签串太长,not check.")
				out=uuid.uuid3(uuid.NAMESPACE_URL, out)

			return out


		def _wrap(*args,**kw):
			# print("_wrap")
			# print("*args2=>",*args)
			# print("**kw2=>",**kw)
			# what=None
			# if len(args)>0:
			# 	what=args[0]


			if isinstance(what,(MethodType,FunctionType)):
				#print("what=>",what)
				#print( hasattr(what,"_result"))

				signstr=get_sign(*args,**kw)
				# print("signstr=>",signstr)

				if not hasattr(what,"_result"):
					what._result={}
					what._dispatch={}

				ca=what._result.get(signstr,None)
				#print("ca=>",ca)

				if ca is None:
					cur=time.time()
					ca=what()
					what._result[signstr]=ca
					what._dispatch[signstr]=cur

					return ca
				else:
					last=what._dispatch[signstr]
					cur=time.time()
					#print(cur-last,self.args)
					if cur-last>self.args:
						print("超出有效时间=>%ss"%self.args)
						ca=what()
						what._result[signstr]=ca
						what._dispatch[signstr]=cur

						return ca

					else:
						print("有效时间内=>%ss"%self.args)
						return ca


		



		if not isinstance(self.args,(MethodType,FunctionType)):
			return _wrap
		else:

			# signstr=self.args.__name__
			# #print("signstr=>",signstr)
			# #print("result before=>",self._result)

			signstr=get_sign(*args,**kw)

			if not hasattr(self.args,"_result"):
				self.args._result={}
				self.args._dispatch={}


			ca=self.args._result.get(signstr)

			if ca is None:
				ca=self.args()
				# #print("res=>",res)
				self.args._result[signstr]=ca
				self.args._dispatch[signstr]=time.time()

			return ca

		





class safe_cached(cached):

	# @lock
	def __call__(self,what=None):
		return super(self,safe_cached).__call__(self,what)




@cached
def test_cached():
	time.sleep(2)
	return "OK"

@cached(8)
def test_cached2():
	time.sleep(4)
	return "OK"


def test_1():
	res=test_cached()


	#print("res=>",res,"\n*****************")

	res3=test_cached()
	#print("res3=>",res3)

	res4=test_cached()
	#print("res4=>",res4)

def test_2():

	#print("1=>",test_cached2())

	# time.sleep(8)
	time.sleep(7)
	#print("第二次取值")
	#print("2=>",test_cached2())



if __name__=="__main__":
	print("res=>",test_cached2())

	# print("wait")
	# time.sleep(6)
	print("res=>",test_cached2())

