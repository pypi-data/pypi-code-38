'''

Copyright (C) 2019 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

import os

def get_working_dir(working_dir):
    '''based on a list (possibly empty), extract the working directory
       and convert to PWD if . is provided.

       Parameters
       ==========
       working_dir: the working directory arglist (e.g., ["."])
    '''
    if working_dir:
        if isinstance(working_dir, list):
            working_dir = working_dir.pop(0)   
            if working_dir == ".":
                working_dir = os.getcwd()

    return working_dir
