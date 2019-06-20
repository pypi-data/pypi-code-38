# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (c) 2017-2019 Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$
__all__ = [
	'numpy',
	'Image', 'ImageGrab', 'ImageDraw', 'ImageFont',
]

import sys

from . import DependencyManagement; from .DependencyManagement import Import, Define, RegisterVersion

numpy = Import( 'numpy', registerVersion=True )

Image     = Import( 'Image',     'PIL.Image',     packageName=[ 'PIL', 'pillow' ] )
ImageGrab = Import( 'ImageGrab', 'PIL.ImageGrab', packageName=[ 'PIL', 'pillow' ] )
ImageDraw = Import( 'ImageDraw', 'PIL.ImageDraw', packageName=[ 'PIL', 'pillow' ] )
ImageFont = Import( 'ImageFont', 'PIL.ImageFont', packageName=[ 'PIL', 'pillow' ] )
if Image:
	RegisterVersion( name='pillow', value=getattr( Image, 'PILLOW_VERSION', None ) )
	RegisterVersion( sys.modules.get( 'PIL', None ) )
	RegisterVersion( Image, 'VERSION' )

if ImageFont:
	try:
		ImageFont.truetype( 'blah', 12 )  # With some broken installations, you can get an ImportError at *this* point due to missing binary components
	except ImportError as err: # so...
		ImageFont = DependencyManagement.ModuleNotAvailable( 'PIL.ImageFont', packageName=[ 'PIL', 'pillow' ], broken=str( err ) )
	except:
		pass  # and sure, you can't find 'blah' font. That's OK.

# Define but don't import yet (used less often for more specialized purposes, and might be slow to import)
Define( 'IPython', packageName='ipython', registerVersion=True )
Define( 'matplotlib', registerVersion=True )
Define( 'cv2', packageName='opencv-python', registerVersion=True ) # used in Shady.Video submodule and Shady.Utilities.VideoRecording class
Define( 'serial', packageName='pyserial', registerVersion=True )   # used for Shady.BitsSharp
