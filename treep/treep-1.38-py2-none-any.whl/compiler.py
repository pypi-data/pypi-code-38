# Treep, copyright 2019 Max Planck Gesellschaft
# Author : Vincent Berenz 

# This file is part of Treep.

#    Treep is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Treep is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Treep.  If not, see <https://www.gnu.org/licenses/>.


import os,copy,sys

from .catkin_make import get_catkin_make_command
from .cmake import get_cmake_command
from .pip import get_pip_command

if sys.version.startswith("2"):
    from .read_compilation_file_python2 import read_compilation_file
else :
    from .read_compilation_file_python3 import read_compilation_file

class Compiler:

    CMAKE = 1
    PIP = 2
    CATKIN_MAKE = 3

    COMPILATION_TYPES = [CMAKE,PIP,CATKIN_MAKE]
    
    YAML_TAGS = { "catkin":CATKIN_MAKE,
                  "cmake":CMAKE,
                  "pip":PIP }
    
    FUNCTIONS = { CATKIN_MAKE: get_catkin_make_command,
                  CMAKE: get_cmake_command,
                  PIP: get_pip_command }

    def __init__(self):

        self.configurations = {}

        for k,v in self.YAML_TAGS.items():
            self.configurations[k] = (v,{})

    # some compilation scripts are natively supported
    # (catkin,cmake,pip)
    # but users have the option to create new ones,
    # expected to be in the treep_xxx/compilation.py
    # file. Importing them here
    def add_compilation_script(self,path):

        imported = read_compilation_file(path)

        # upgrading locals with content of the compilation
        # file. Making sure already existing locals are not
        # overwritten
        for k,v in imported.items():
            if str(k) not in locals():
                locals()[str(k)]=v
            else :
                raise Exception("Failed to run the compilation script: "+str(path)+":\n"
                                +"It would overwrite the local variable '"+str(k)+"'")
        
        # new non private variables
        new_functions = {k:v for k,v in imported.items()
                         if not k.startswith("_")}

        # new callables
        new_functions = {k:v for k,v in new_functions.items()
                         if hasattr(v,'__call__')}
        
        # adding each function to Compiler
        for name,function in new_functions.items():

            # creating a new compilation type
            index = min(self.__class__.COMPILATION_TYPES)-1
            setattr(self.__class__,name,index)
            self.__class__.COMPILATION_TYPES.append(index)
            
            # adding a new yaml tag
            self.__class__.YAML_TAGS[name]=index

            # adding a new function
            self.__class__.FUNCTIONS[index]=function

            # adding a configuration
            self.configurations[name]=(index,{})
            

    # category: catkin_make, cmake or pip
    def add(self,label,category,kwargs):

        self.configurations[label]=[category,kwargs]
        
        
    def get_script(self,
                   workspace_path,
                   package_name,
                   package_path,
                   label,
                   config={},
                   return_function=False):

        category,kwargs = self.configurations[label]

        # the yaml configuration file provides some configuration
        # for calling the script. Here possibly overwriting them.
        for k,v in config.items():
            kwargs[k]=v

        function = self.FUNCTIONS[category]
            
        if return_function:
            return ( function,
                     [ workspace_path,
                       package_name,
                       package_path],
                     kwargs )

        return function( workspace_path,
                         package_name,
                         package_path,
                         **kwargs )
        

