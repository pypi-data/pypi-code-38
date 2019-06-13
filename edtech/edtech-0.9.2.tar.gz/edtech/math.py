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
@summary: Helper function to convert a string to float, ignoring any exceptions but returning default value if one occurred.
'''
def strToFloat(inStr, default):
    try:
        return float(inStr)
    except:
        return default

'''
@summary: Helper function to calculate median
'''
def median( in_list ):    
    # convert all values to floats
    index = 0
    while (index < len(in_list)):
        try:
            in_list[index] = float( in_list[index] )
            index = index + 1
        except exceptions.ValueError:
            in_list.pop( index )

    # sort the remaining list
    in_list.sort( )

    # if the list is empty, return
    if ( len( in_list ) == 0 ):
        return None

    if ( len( in_list ) % 2 == 1 ):
        # odd count
        return in_list[( len( in_list ) + 1 ) / 2 - 1 ]
    else:
        # even count
        upper = in_list[ len( in_list ) / 2 ]
        lower = in_list[ len( in_list ) / 2 - 1 ]
        return ( upper + lower ) / 2

'''
@summary: Helper function to calculate mode
'''
def mode( in_list ):
    
    for i in range( 0, len( in_list )):
        try:
            in_list[i] = float( in_list[i] )
        except exceptions.ValueError:
            in_list.pop( i )

    unique_val_list = list( set(in_list) )
    
    # If there are no unique values, return None
    if len( unique_val_list ) == 0:
        return None

    count = [0] * len(unique_val_list)

    for i in range( len(count) ):
        count[i] = in_list.count( unique_val_list[i] )

    best_list = [0]

    for i in range( 1, len(count) ):
        if( count[i] == count[ best_list[0] ] ):
            best_list.append( i )
        elif( count[i] > count[ best_list[0] ] ):
            del best_list[:]
            best_list.append(i)

    best_val_list = [ unique_val_list[i] for i in best_list ]

    return median( best_val_list )

'''
@summary: Helper function to calculate mode of a string (eventually merge with above)
'''
def strmode( in_list ):

    for i in range( 0, len( in_list )):
        try:
            in_list[i] = str( in_list[i] )
        except exceptions.ValueError:
            in_list.pop( i )

    unique_val_list = list( set(in_list) )
    
    # If there are no unique values, return None
    if len( unique_val_list ) == 0:
        return None

    count = [0] * len(unique_val_list)

    for i in range( len(count) ):
        count[i] = in_list.count( unique_val_list[i] )

    best_list = [0]

    for i in range( 1, len(count) ):
        if( count[i] == count[ best_list[0] ] ):
            best_list.append( i )
        elif( count[i] > count[ best_list[0] ] ):
            del best_list[:]
            best_list.append(i)

    best_val_list = [ unique_val_list[i] for i in best_list ]

    return best_val_list[0]
