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

import os
from . import treep_git

# return a status for each repo find under all folders contained in path

def get_statuses(path):

    repo_paths = []
    
    for current, directories, files in os.walk(path,topdown=True):

        if ".git" in directories :

            repo_paths.append(current)

            directories[:] = []

    return [ treep_git.get_status(path) for path in repo_paths ]

        
        
        
