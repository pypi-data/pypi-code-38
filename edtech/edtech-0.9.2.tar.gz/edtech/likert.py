'''
This file is part of the EdTech library project at Full Sail University.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

    Copyright (C) 2014, 2015 Full Sail University.
'''

import exceptions

'''
@summary: Helper function to convert a numeric string to a Likert string
'''
def toLikert(value, scale):
    # convert the string to a float
    try:
        value = float(value)
    except exceptions.ValueError:
        return "-1"

    for limit in sorted(scale.keys(), reverse=True):
        if (value >= limit):
            return scale[limit]
    
    return "-1"

'''
@summary: Helper function to convert a Likert string to a number value
'''
def getLikertKey(value, scale):
    # convert the string to a float
    try:
        value = str(value).lower()
    except exceptions.ValueError:
        return "-1"

    for limit, likertString in scale.items():
        if (value == likertString.lower()):
            return limit
    
    return "-1"

'''
@summary: Helper function to convert a numeric string to a Likert index
'''
def getLikertIndex(value, scale):
    # convert the string to a float
    if isinstance(value, basestring):
        return sorted(scale.values()).index(value)
    elif isinstance(value, (int, long, float)):
        try:
            return sorted(scale.keys()).index(value)
        except:
            return -1
    else:
        return -1
