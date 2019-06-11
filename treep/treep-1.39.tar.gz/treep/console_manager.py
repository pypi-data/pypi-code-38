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

from __future__ import print_function

from . import coloring


class Console_manager(object):

    
    __slots__ = ["errors","warnings"]

    
    def __init__(self):

        self.errors = {}
        self.warnings = {}

        
    def add_warning(self,message,error):
        self.warnings[message]=error

        
    def add_error(self,message,error):
        self.errors[message]=error

        
    def console(self):

        if self.errors:
            print(coloring.red("\n\t| [ERRORS]"),end='')
            print(coloring.red("\n\t|"))
            for message,error in self.errors.items():
                error = error.replace('\n',' ; ')
                print("\t"+coloring.red("|")+"\t"+coloring.red(message)+" "+coloring.dim(error))
            print ("\n")

        if self.warnings:
            print(coloring.orange("\n\t[WARNINGS]"),end='')
            print(coloring.orange("\n\t|"))
            for message,error in self.warnings.items():
                error = error.replace('\n',' ; ')
                print("\t"+coloring.orange("|")+"\t"+coloring.orange(message)+" "+coloring.dim(error))
            print ("\n")
