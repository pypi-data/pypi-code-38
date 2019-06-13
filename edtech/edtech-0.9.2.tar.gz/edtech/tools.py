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

import random
import string

global stringCodecs
defaultCodecs = ['utf8', 'cp437']

def getRandomPassword(rangeLow = 7, rangeHigh = 16):
    size = int(round(random.SystemRandom().uniform(rangeLow, rangeHigh)))
    return ''.join(random.SystemRandom().choice(string.uppercase + string.lowercase + string.digits) for _ in xrange(size))

def transposeData(dataset):
    return [list(i) for i in zip(*dataset)]

#def warning(*objs):
#    print("WARNING: ", *objs, file=sys.stderr)
    
def decodeString(value, codecs=defaultCodecs):
    for encoding in codecs:
        try:
            return value.decode(encoding)
        except:
            pass
    print("Couldn't decode string: " + value)

