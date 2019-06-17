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
from . import ArgDefine
from . import ArgElement
from . import ArgSection
from . import ArgVolatile
from . import ArgDefine

##
## @brief Class to define the agmument list availlable for a program
##
class Arguments:
	##
	## @brief Constructor.
	## @param[in] self Class handle
	##
	def __init__(self):
		self.list_properties = []
		self._list_element_stop = []
		self._last_element_parsed = 0
	
	##
	## @brief Add a new argument possibilities...
	## @param[in] self Class handle
	## @param[in] smallOption (char) Value for the small option ex: '-v' '-k' ... 1 single char element (no need of '-')
	## @param[in] bigOption (string) Value of the big option name ex: '--verbose' '--kill' ... stated with -- and with the full name (no need of '--')
	## @param[in] list ([[string,string],...]) Optionnal list of availlable option: '--mode=debug' ==> [['debug', 'debug mode'],['release', 'release the software']]
	## @param[in] desc (string) user friendly description with this parameter (default "")
	## @param[in] haveParam (bool) The option must have a parameter (default False)
	##
	def add(self, smallOption="", bigOption="", list=[], desc="", haveParam=False):
		self.list_properties.append(ArgDefine.ArgDefine(smallOption, bigOption, list, desc, haveParam))
	
	def add_arg(self, destOption="", optionnal=False, desc=""):
		self.list_properties.append(ArgVolatile.ArgVolatile(destOption, optionnal, desc))
	
	##
	## @brief Add section on argument list
	## @param[in] self Class handle
	## @param[in] sectionName (string) Name of the cestion ex: "option" is displayed [option]
	## @param[in] sectionDesc (string) Comment assiciated with the group
	##
	def add_section(self, sectionName, sectionDesc):
		self.list_properties.append(ArgSection.ArgSection(sectionName, sectionDesc))
	
	##
	## @brief Parse the argument set in the command line
	## @param[in] self Class handle
	## @param[in] start_position_parsing position to start the parsing in the arguments
	##
	def parse(self, start_position_parsing=1, have_unknow_argument=False):
		list_argument = [] # composed of list element
		not_parse_next_element=False
		for iii in range(start_position_parsing, len(sys.argv)):
			self._last_element_parsed = iii
			# special case of parameter in some elements
			if not_parse_next_element == True:
				not_parse_next_element = False
				continue
			debug.verbose("parse [" + str(iii) + "]=" + sys.argv[iii])
			argument = sys.argv[iii]
			# check if we get a stop parsing element:
			if argument in self._list_element_stop:
				debug.warning("stop at position: " + str(iii))
				list_argument.append(ArgElement.ArgElement("", argument))
				break;
			optionList = argument.split("=")
			debug.verbose(str(optionList))
			if type(optionList) == type(str()):
				option = optionList
			else:
				option = optionList[0]
			optionParam = argument[len(option)+1:]
			debug.verbose(option)
			argument_found=False;
			if option[:2] == "--":
				# big argument
				for prop in self.list_properties:
					if prop.is_parsable()==False:
						continue
					if prop.get_option_big()=="":
						continue
					if prop.get_option_big() == option[2:]:
						# find it
						debug.verbose("find argument 2 : " + option[2:])
						if prop.need_parameters()==True:
							internalSub = option[2+len(prop.get_option_big()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.get_option_big() + "' cmdLine='" + argument + "'")
									prop.display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									not_parse_next_element=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.get_option_big() + "' Missing : subParameters ... cmdLine='" + argument + "'")
									prop.display()
									exit(-1)
							if prop.check_availlable(optionParam)==False:
								debug.warning("argument error : '" + prop.get_option_big() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.display()
								exit(-1)
							list_argument.append(ArgElement.ArgElement(prop.get_option_big(),optionParam))
							argument_found = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.get_option_big() + "' need no subParameters : '" + optionParam + "'   cmdLine='" + argument + "'")
								prop.display()
							list_argument.append(ArgElement.ArgElement(prop.get_option_big()))
							argument_found = True
						break;
				if argument_found == False:
					if have_unknow_argument == False:
						debug.error("UNKNOW argument : '" + argument + "'")
			elif option[:1]=="-":
				# small argument
				for prop in self.list_properties:
					if prop.is_parsable()==False:
						continue
					if prop.get_option_small()=="":
						continue
					if prop.get_option_small() == option[1:1+len(prop.get_option_small())]:
						# find it
						debug.verbose("find argument 1 : " + option[1:1+len(prop.get_option_small())])
						if prop.need_parameters()==True:
							internalSub = option[1+len(prop.get_option_small()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.get_option_big() + "' cmdLine='" + argument + "'")
									prop.display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									not_parse_next_element=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.get_option_big() + "' Missing : subParameters  cmdLine='" + argument + "'")
									prop.display()
									exit(-1)
							if prop.check_availlable(optionParam)==False:
								debug.warning("argument error : '" + prop.get_option_big() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.display()
								exit(-1)
							list_argument.append(ArgElement.ArgElement(prop.get_option_big(),optionParam))
							argument_found = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.get_option_big() + "' need no subParameters : '" + optionParam + "'  cmdLine='" + argument + "'")
								prop.display()
							list_argument.append(ArgElement.ArgElement(prop.get_option_big()))
							argument_found = True
						break;
			
			if argument_found==False:
				# small argument
				for prop in self.list_properties:
					if    prop.is_parsable() == True \
					   or prop.get_option_big() == "":
						continue
					if prop.need_parameters() == True:
						list_argument.append(ArgElement.ArgElement(prop.get_option_big(), argument))
						argument_found = True
						break
			if argument_found==False:
				#unknow element ... ==> just add in the list ...
				debug.verbose("unknow argument : " + argument)
				list_argument.append(ArgElement.ArgElement("", argument))
			
		for prop in self.list_properties:
			if    prop.is_parsable() == True \
			   or prop.get_option_big() == "":
				continue
			if     prop.need_parameters() == True \
			   and prop.optionnal == False:
				debug.error("Missing argument:" + prop.get_option_big())
		#for argument in list_argument:
		#	argument.display()
		#exit(0)
		return list_argument;
	
	##
	## @brief Stop parsing at a specific position
	## @param[in] self Class handle
	## @param[in] list_of_element List of element that stop the parsing
	##
	def set_stop_at(self, list_of_element):
		self._list_element_stop = list_of_element
	
	##
	## @brief get the last element parsed.
	## @param[in] self Class handle
	##
	def get_last_parsed(self):
		return self._last_element_parsed
	
	##
	## @brief Display help on console output
	## @param[in] self Class handle
	## @param[in] action_name opation to set at the end of the application name
	##
	def display(self, action_name=""):
		print("usage:")
		listOfPropertiesArg = "";
		for element in self.list_properties :
			listOfPropertiesArg += element.get_porperties()
		print("	" + sys.argv[0] + " " + action_name + " " + listOfPropertiesArg + " ...")
		for element in self.list_properties :
			element.display()

