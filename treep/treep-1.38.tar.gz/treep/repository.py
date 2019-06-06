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


from . import coloring


class Repository(object):

    def __init__( self,
                  name,
                  origin,
                  path,
                  branch="master",
                  commit=None,
                  tag=None,
                  compilation=None) :

        if path is None:
            path = ''

        self.name = name
        self.origin = origin
        self.path = path
        self.branch = branch
        self.commit = commit
        self.tag = tag
        self.compilation = compilation


