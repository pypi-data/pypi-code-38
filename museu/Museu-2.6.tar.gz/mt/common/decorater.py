#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-10 15:16:29
# @Author  : Blackstone
# @to      :

from types import MethodType,FunctionType
import time


class decorater(object):

	_subscriber_pool={}
	_singlton_storage={}

	@staticmethod
	def lock(func):

		import threading
		func._lock=threading.Lock()
		def wrap(*args,**kw):
			with func._lock:
				return func(*args,**kw)
		return wrap


	@classmethod
	def publisher(cls,name):
		
		def wrap(classname):

			subscribers=cls._subscriber_pool.get(name)
			#print(subscribers)
			classname.update=lambda self,a=None:[x.notify(msg=a)   for x in cls._subscriber_pool.get(name)]
			return classname
		return wrap
			

	@classmethod
	def subscriber(cls,name):
		def wrap(classname):
			instance=classname()
			if cls._subscriber_pool.get(name) is None:
				cls._subscriber_pool[name]=[instance]
			else:
				cls._subscriber_pool[name].append(instance)

			# classname.notify=lambda a:print(1) or print(2)
			return classname
		return wrap



	@classmethod
	def singleton(cls,classname):
		def wrap(*args,**kw):
			
			_instance=decorater._singlton_storage.get(classname,None)
			
			if _instance is None:
				_instance=classname(*args,**kw)
				decorater._singlton_storage[classname]=_instance

			#print("********************************\n",_instance)

			return _instance

		return wrap

	
	@classmethod
	def safe_singleton(cls,classname):
		@decorater.lock
		def wrap(*args,**kw):
			
			_instance=decorater._singlton_storage.get(classname,None)
			
			if _instance is None:
				_instance=classname(*args,**kw)
				decorater._singlton_storage[classname]=_instance

			#print("********************************\n",_instance)

			return _instance

		return wrap



	# def cached(func):

	# 	def init():
	# 		pass

	# 	def get_sign(*str_):
	# 		out=""
	# 		for _ in str_:
	# 			out+=str(_)

	# 		import uuid,warnings
	# 		if len(out)>1000000000:
	# 			warnings.warn("签串太长,not check.")
	# 			out=uuid.uuid3(uuid.NAMESPACE_URL, out)

	# 		return out


		
	# 	def wrap(*args,**kw):
	# 		# print("*"*100)
	# 		# print("func=>",func)
	# 		# print("args=>",args)
	# 		# print("kw=>",kw)

	# 		sign=get_sign(args,kw)

	# 		log("函数签名=>%s"%sign)

	# 		if not hasattr(func,"_cache"):
	# 			func._cache={}

				

	# 		if func._cache.get(sign) is None:
	# 			func._cache[sign]=func(*args,**kw)


	# 		return func._cache.get(sign)


	# 	return wrap


	@classmethod
	def test_time(cls,func):
		def wrap(*args,**kw):

			print(cls)
			import time
			v1=time.time()

			re=func(*args,**kw)
			v2=time.time()

			log("Function %s spend %s sec. "%(func,v2-v1))
			return re

		return wrap



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
							#print("c超出有效时间")
							ca=what()
							what._result[signstr]=ca
							what._dispatch[signstr]=cur

							return ca

						else:
							#print("有效时间内")
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
				





	# class safe_cached(cached):
		

	# 	@decorater.lock
	# 	def __call__(self,what=None):
	# 		return super(self,safe_cached).__call__(self,what)


