#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##
import sys
from realog import debug

##
## @brief Declare a possibility of an argument value
##
class ArgDefine:
	##
	## @brief Contructor.
	## @param[in] self Class handle
	## @param[in] smallOption (char) Value for the small option ex: '-v' '-k' ... 1 single char element (no need of '-')
	## @param[in] bigOption (string) Value of the big option name ex: '--verbose' '--kill' ... stated with -- and with the full name (no need of '--')
	## @param[in] list ([[string,string],...]) Optionnal list of availlable option: '--mode=debug' ==> [['debug', 'debug mode'],['release', 'release the software']]
	## @param[in] desc (string) user friendly description with this parameter (default "")
	## @param[in] haveParam (bool) The option must have a parameter (default False)
	##
	def __init__(self,
	             smallOption="", # like v for -v
	             bigOption="", # like verbose for --verbose
	             list=[], # ["val", "description"]
	             desc="",
	             haveParam=False):
		self.option_small = smallOption;
		self.option_big = bigOption;
		self.list = list;
		if len(self.list)!=0:
			self.have_param = True
		else:
			if True==haveParam:
				self.have_param = True
			else:
				self.have_param = False
		self.description = desc;
	
	def is_parsable(self):
		return True
	##
	## @brief Get the small name of the option ex: '-v'
	## @param[in] self Class handle
	## @return (string) Small name value
	##
	def get_option_small(self):
		return self.option_small
	
	##
	## @brief Get the big name of the option ex: '--verbose'
	## @param[in] self Class handle
	## @return (string) Big name value
	##
	def get_option_big(self):
		return self.option_big
	
	##
	## @brief Get the status of getting user parameter value
	## @param[in] self Class handle
	## @return True The user must write a value
	## @return False The user must NOT write a value
	##
	def need_parameters(self):
		return self.have_param
	
	##
	## @brief Compatibility with @ref ArgSection class
	## @param[in] self Class handle
	## @return (string) empty string
	##
	def get_porperties(self):
		return ""
	
	##
	## @brief Check if the user added value is correct or not with the list of availlable value
	## @param[in] self Class handle
	## @param[in] argument (string) User parameter value (string)
	## @return True The parameter is OK
	## @return False The parameter is NOT Availlable
	##
	def check_availlable(self, argument):
		if len(self.list)==0:
			return True
		for element,desc in self.list:
			if element == argument:
				return True
		return False
	
	##
	## @brief Display the argument property when user request help
	## @param[in] self Class handle
	##
	def display(self):
		color = debug.get_color_set()
		if self.option_small != "" and self.option_big != "":
			print("		" + color['red'] + "-" + self.option_small + "" + color['default'] + " / " + color['red'] + "--" + self.option_big + color['default'])
		elif self.option_small != "":
			print("		" + color['red'] + "-" + self.option_small + color['default'])
		elif self.option_big != "":
			print("		" + color['red'] + "--" + self.option_big + color['default'])
		else:
			print("		???? ==> internal error ...")
		if self.description != "":
			print("			" + self.description)
		if len(self.list)!=0:
			hasDescriptiveElement=False
			for val,desc in self.list:
				if desc!="":
					hasDescriptiveElement=True
					break;
			if hasDescriptiveElement==True:
				for val,desc in self.list:
					print("				" + val + " : " + desc)
			else:
				tmpElementPrint = ""
				for val,desc in self.list:
					if len(tmpElementPrint)!=0:
						tmpElementPrint += " / "
					tmpElementPrint += val
				print("				{ " + tmpElementPrint + " }")
