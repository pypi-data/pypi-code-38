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


import subprocess


def execute(command, shell=True):
    try:
        out = subprocess.check_output( command,
                                       stderr=subprocess.STDOUT,
                                       shell=shell )
    except Exception as e:
        out = e.output

    try :
        # python 3
        out = out.decode("utf-8") 
    except :
        # python 2.7
        pass
        
    return out

