#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
from netbluemind.python import serder
from enum import Enum

class SearchSortOrder(Enum):
    Asc = 'Asc';
    Desc = 'Desc';

class __SearchSortOrderSerDer__:
    def __init__( self):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = SearchSortOrder[value]
        return instance


    def encode(self, value):
        if(value == None):
            return None
        instance = value.value
        return instance
