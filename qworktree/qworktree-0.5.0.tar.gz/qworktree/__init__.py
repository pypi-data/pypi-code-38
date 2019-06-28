#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2019, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##
import os
import sys
import fnmatch
import copy
from realog import debug
# Local import
from . import tools
from . import env
from . import arguments


debug.set_display_on_error(   "******************************************************\n"
                            + "**            ERROR              ERROR              **\n"
                            + "******************************************************")

def filter_name_and_file(root, list_files, filter):
	# filter elements:
	tmp_list = fnmatch.filter(list_files, filter)
	out = []
	for elem in tmp_list:
		if os.path.isfile(os.path.join(root, elem)) == True:
			out.append(elem);
	return out;

def filter_path(root, list_files):
	out = []
	for elem in list_files:
		if    len(elem) == 0 \
		   or elem[0] == '.':
			continue
		if os.path.isdir(os.path.join(root, elem)) == True:
			out.append(elem);
	return out;

def import_path_local(path, limit_sub_folder, exclude_path = [], base_name = ""):
	out = []
	debug.verbose("qworktree files: " + str(path) + " [START]")
	if limit_sub_folder == 0:
		debug.debug("Subparsing limitation append ...")
		return []
	list_files = os.listdir(path)
	try:
		list_files = os.listdir(path)
	except:
		# an error occure, maybe read error ...
		debug.warning("error when getting subdirectory of '" + str(path) + "'")
		return []
	if path in exclude_path:
		debug.debug("find '" + str(path) + "' in exclude_path=" + str(exclude_path))
		return []
	# filter elements:
	tmp_list_qworktree_file = filter_name_and_file(path, list_files, base_name + "*.py")
	debug.verbose("qworktree files: " + str(path) + " : " + str(tmp_list_qworktree_file))
	# Import the module:
	for filename in tmp_list_qworktree_file:
		out.append(os.path.join(path, filename))
		debug.extreme_verbose("     Find a file : '" + str(out[-1]) + "'")
	need_parse_sub_folder = True
	rm_value = -1
	# check if the file "qworktree_parse_sub.py" is present ==> parse SubFolder (force and add +1 in the resursing
	if base_name + "ParseSubFolders.txt" in list_files:
		debug.debug("find SubParser ... " + str(base_name + "ParseSubFolders.txt") + " " + path)
		data_file_sub = tools.file_read_data(os.path.join(path, base_name + "ParseSubFolders.txt"))
		if data_file_sub == "":
			debug.debug("    Empty file Load all subfolder in the worktree in '" + str(path) + "'")
			need_parse_sub_folder = True
			rm_value = 0
		else:
			list_sub = data_file_sub.split("\n")
			debug.debug("    Parse selected folders " + str(list_sub) + " no parse local folder directory")
			need_parse_sub_folder = False
			for folder in list_sub:
				if    folder == "" \
				   or folder == "/":
					continue;
				tmp_out = import_path_local(os.path.join(path, folder),
				                            1,
				                            exclude_path,
				                            base_name)
				# add all the elements:
				for elem in tmp_out:
					out.append(elem)
	if need_parse_sub_folder == True:
		list_folders = filter_path(path, list_files)
		for folder in list_folders:
			tmp_out = import_path_local(os.path.join(path, folder),
			                            limit_sub_folder - rm_value,
			                            exclude_path,
			                            base_name)
			# add all the elements:
			for elem in tmp_out:
				out.append(elem)
	return out



my_args = arguments.qworktreeArg()
my_args.add_section("option", "Can be set one time in all case")
my_args.add("h", "help", desc="Display this help")
my_args.add("v", "verbose", list=[["0","None"],["1","error"],["2","warning"],["3","info"],["4","debug"],["5","verbose"],["6","extreme_verbose"]], desc="display debug level (verbose) default =2")
my_args.add("c", "color", desc="Display message in color")
local_argument = my_args.parse()

##
## @brief Display the help of this makefile.
##
def usage():
	color = debug.get_color_set()
	# generic argument displayed : 
	my_args.display()
	print("		Action availlable" )
	print("	ex: " + sys.argv[0] + " -c init http://github.com/atria-soft/manifest.git")
	print("	ex: " + sys.argv[0] + " sync")
	exit(0)

def check_boolean(value):
	if    value == "" \
	   or value == "1" \
	   or value == "true" \
	   or value == "True" \
	   or value == True:
		return True
	return False

# preparse the argument to get the verbose element for debug mode
def parseGenericArg(argument, active):
	debug.extreme_verbose("parse arg : " + argument.get_option_name() + " " + argument.get_arg() + " active=" + str(active))
	if argument.get_option_name() == "help":
		if active == False:
			usage()
		return True
	elif argument.get_option_name()=="jobs":
		if active == True:
			#multiprocess.set_core_number(int(argument.get_arg()))
			pass
		return True
	elif argument.get_option_name()=="depth":
		if active == True:
			env.set_parse_depth(int(argument.get_arg()))
		return True
	elif argument.get_option_name() == "verbose":
		if active == True:
			debug.set_level(int(argument.get_arg()))
		return True
	elif argument.get_option_name() == "color":
		if active == True:
			if check_boolean(argument.get_arg()) == True:
				debug.enable_color()
			else:
				debug.disable_color()
		return True
	elif argument.get_option_name() == "no-fetch-manifest":
		if active == False:
			env.set_fetch_manifest(False)
		return True
	return False

# parse default unique argument:
for argument in local_argument:
	parseGenericArg(argument, True)

__base_element_name = env.get_system_base_name() + "_"

tmp_out = import_path_local(tools.get_run_path(),
                            3,
                            [],
                            __base_element_name)



def get_element_name(_path):
	base_name = os.path.basename(_path)
	debug.verbose(" path: '" + _path + "' ==> basename='" + base_name + "'")
	if len(base_name) <= 3 + len(__base_element_name):
		# reject it, too small
		return None
	base_name = base_name[:-3]
	if base_name[:len(__base_element_name)] != __base_element_name:
		# reject it, wrong start file
		return None
	debug.verbose("    ==> '" + base_name[len(__base_element_name):] + "'")
	return base_name[len(__base_element_name):]

def get_element_depend(_path):
	sys.path.append(os.path.dirname(_path))
	name = get_element_name(_path)
	the_element = __import__(__base_element_name + name)
	if "depend_on" in dir(the_element):
		return the_element.depend_on
	return []

debug.info("======================================================")
debug.info("== Create project element")
debug.info("======================================================")
project_elements = []

for elem in tmp_out:
	dependency = get_element_depend(elem)
	name = get_element_name(elem)
	project_elements.append({
		"file": elem,
		"name": name,
		"dependency": copy.deepcopy(dependency),
		"dependency2": copy.deepcopy(dependency)
		})
	debug.info("--------------------------------------------------------------------------------------------------")
	debug.info("Element:        '" + name + "'            in path='" + elem + "'")
	debug.info("    depends:    " + str(dependency))

debug.info("======================================================")
debug.info("== Check if all dependency are availlable")
debug.info("======================================================")
list_of_library = []
missing_dependency = []
for elem in tmp_out:
	name = get_element_name(elem)
	if name not in list_of_library:
		list_of_library.append(name)
for elem in tmp_out:
	dependency = get_element_depend(elem)
	name = get_element_name(elem)
	for dep in dependency:
		if dep not in list_of_library:
			if dep not in missing_dependency:
				missing_dependency.append(dep)
			debug.info("Element:        '" + name + "'")
			debug.warning("    depends:    " + str(dependency))
			debug.warning("    missing:    " + str(dep))
if len(missing_dependency) != 0:
	debug.error("missing dependency: " + str(missing_dependency))

debug.info("======================================================")
debug.info("== Ordering elements")
debug.info("======================================================")
project_elements_ordered = []

max_loop = len(project_elements) * 10

while len(project_elements) != 0:
	max_loop -= 1
	if max_loop <= 0:
		debug.error("ERROR: Detect dependency loop...")
	debug.info("Order dependency: " + str(len(project_elements)) + "    ->    " + str(len(project_elements_ordered)))
	for elem in project_elements:
		debug.info("    " + elem["name"] + "   " + str(len(elem["dependency2"])))
		if len(elem["dependency2"]) == 0:
			debug.info("        Add element: '" + elem["name"] + "'")
			project_elements_ordered.append(copy.deepcopy(elem))
			project_elements.remove(elem)
	for elem in project_elements:
		debug.info("    clean " + elem["name"])
		for dep in elem["dependency2"]:
			for elem_ordered in project_elements_ordered:
				if dep == elem_ordered["name"]:
					elem["dependency2"].remove(dep)
					break
	

"""
for elem in tmp_out:
	debug.info("find : " + elem)
	name = get_element_name(elem)
	dependency = get_element_depend(elem)
	relative_file = os.path.dirname(os.path.relpath(elem, tools.get_run_path()))
	debug.info("    rel_path=" + relative_file)
	debug.info("    name=" + name)
	debug.info("    depends=" + str(dependency))
"""

debug.info("Ordering done: " + str(len(project_elements)) + "    ->    " + str(len(project_elements_ordered)))
#project_elements_ordered.reverse()


out = "# Automatic generation with qworktree ... \n"
out += "TEMPLATE = subdirs\n"
out += "\n"
out += "load(root_directory.prf)\n"
out += "\n"
out += "#import folders\n"
out += "SUBDIRS += \\\n"
for elem in project_elements_ordered:
	#relative_file = os.path.dirname(os.path.relpath(elem, tools.get_run_path()))
	#out += "    " + relative_file + " \\\n"
	out += "    " + elem["name"] + " \\\n"

out += "\n"


out += "# build the project sequentially as listed in SUBDIRS !\n"
out += "CONFIG += ordered\n"

out += "\n"
out += "#define every folders\n"
for elem in project_elements_ordered:
	relative_file = os.path.dirname(os.path.relpath(elem["file"], tools.get_run_path()))
	#out += elem["name"] + ".subdir = " + relative_file + "\n"
	out += elem["name"] + ".file = " + relative_file + "/" + elem["name"] + ".pro\n"

out += "\n"
out += "#define dependency\n"

for elem in project_elements_ordered:
	out += "#define dependency of " + elem["name"] + "\n"
	for dep in elem["dependency"]:
		out += name + ".depends = " + dep + "\n"
	out += "\n"
out += "\n"
out += "\n"
out += "\n"

#debug.info(out)
tools.file_write_data(os.path.join(tools.get_run_path(), os.path.basename(tools.get_run_path())+".pro"), out, only_if_new=True)

out = "# Automatic generation with qworktree ... \n"
out += "\n"
for elem in project_elements_ordered:
	relative_file = os.path.dirname(os.path.relpath(elem["file"], tools.get_run_path()))
	out += "LIB_DECLARE_DEPENDENCIES_" + elem["name"].upper() + " = " + os.path.join(relative_file, "dependencies.pri") + "\n"
out += "\n"
out += "\n"
out += "\n"

#debug.info(out)
tools.file_write_data(os.path.join(tools.get_run_path(), "defines.prf"), out, only_if_new=True)

debug.info("Create basic qmake project")


debug.info("======================================================")
debug.info("==                 ALL is GOOD                      ==")
debug.info("======================================================")

