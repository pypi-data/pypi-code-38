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
"""
This module contains various optional (but useful) utility functions
that relate specifically to computation and conversion of contrast
and luminance values.

Note that everything exported from this module is also available in
the top-level `Shady.*` namespace.

Brief definitions for terms used in this submodule are as follows,
but for full details, see :doc:`../auto/LuminanceAndContrast` in the online
documentation or the docstring of `Shady.Documentation.LuminanceAndContrast`.


Ideal luminance:
	a value from 0 (corresponding to the screen's minimum luminance) to 1
	(corresponding to the screen's maximum luminance).

Physical luminance:
	a true physical measure of screen luminance, including the effect of
	reflected ambient light.  Will not ever reach 0 unless your setup is
	*very* expensive...

Ideal contrast ratio:
	a contrast ratio (RMS or Michelson) computed from ideal luminance
	values.

Physical contrast ratio:
	a contrast ratio (RMS or Michelson) computed from physical luminance
	values.

Normalized contrast:
	not a contrast ratio, but rather a scaling factor from 0 to 1 that is
	applied to a signal's amplitude, such that a normalized contrast of 1
	allows the signal to fill the screen's entire luminance range.
"""

__all__ = [
	
	'RMSContrastRatio',
	'MichelsonContrastRatio',
	
	'IdealToPhysicalLuminance',
	'PhysicalToIdealLuminance',
	
	'IdealToPhysicalContrastRatio',
	'PhysicalToIdealContrastRatio',
	
	'IdealContrastRatioToNormalizedContrast',
	'NormalizedContrastToIdealContrastRatio',
	
]
import warnings

from . import Dependencies; from .Dependencies import numpy


def RMSContrastRatio( pixels, background=None ):
	r"""
	Compute the root-mean-square contrast ratio of a pixel array.
	:math:`\frac{\sqrt{\frac{1}{N}\sum_x\sum_y (L_{xy} - L_{\mu})^2}}{L_{\mu}}`,
	or in plain text::
	
	    ( (pixels - background) ** 2 ).mean() ** 0.5   /   background
	
	where `background` (:math:`=L_{\mu}`) defaults to `pixels.mean()`.
	
	If `pixels` is a three-dimensional array, two preprocessing steps are performed:
	first, if its extent in the third dimension is 2 or 4, the last layer is assumed
	to be an alpha channel and is excluded from the computation; second, "luminance"
	is computed as the mean-across-(remaining)-layers. In reality, red, green and blue
	channels will not contribute equally to luminance, so for more accurate results,
	you may wish to perform your own computations to convert the array into a
	single-channel array of luminances before calling this function.
	
	This function will work on any kind of luminance scale: if you feed it ideal
	luminances (in the 0 to 1 range), you will get an "ideal" contrast ratio. If
	you feed it physical luminances (in candelas / m^2) you will get a physical
	contrast ratio. For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of `Shady.Documentation.LuminanceAndContrast`.
	
	See also:
		- `MichelsonContrastRatio()`
		- `IdealToPhysicalContrastRatio()`
		- `PhysicalToIdealContrastRatio()`
	"""
	pixels = numpy.array( pixels, dtype=float, copy=False )
	if pixels.ndim == 3:
		if pixels.shape[ 2 ] in [ 2, 4 ]: pixels = pixels[ :, :, ::-1 ]
		pixels = pixels.mean( axis=2 )
	if background is None: background = pixels.mean()
	return ( ( pixels - background ) ** 2 ).mean() ** 0.5 / background

def MichelsonContrastRatio( pixels, background=None ): # NB: background is unused
	r"""
	Compute the Michelson contrast ratio of a pixel array,
	:math:`\frac{L_{\max} - L_{\min}}{L_{\max} + L_{\min}}`,
	or in plain text::
	
	    (pixels.max() - pixels.min()) / (pixels.max() + pixels.min())
	
	The input argument `background` is unused but it is included in
	the prototype for compatibility with `RMSContrastRatio()`.
	
	If `pixels` is a three-dimensional array, two preprocessing steps are performed:
	first, if its extent in the third dimension is 2 or 4, the last layer is assumed
	to be an alpha channel and is excluded from the computation; second, "luminance"
	is computed as the mean-across-(remaining)-layers. In reality, red, green and blue
	channels will not contribute equally to luminance, so for more accurate results,
	you may wish to perform your own computations to convert the array into a
	single-channel array of luminances before calling this function.
	
	This function will work on any kind of luminance scale: if you feed it ideal
	luminances (in the 0 to 1 range), you will get an "ideal" contrast ratio. If
	you feed it physical luminances (in candelas / m^2) you will get a physical
	contrast ratio. For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of `Shady.Documentation.LuminanceAndContrast`.
	
	See also:
		- `RMSContrastRatio()`
		- `IdealToPhysicalContrastRatio()`
		- `PhysicalToIdealContrastRatio()`
	"""
	pixels = numpy.array( pixels, dtype=float, copy=False )
	if pixels.ndim == 3:
		if pixels.shape[ 2 ] in [ 2, 4 ]: pixels = pixels[ :, :, ::-1 ]
		pixels = pixels.mean( axis=2 )
	pmin, pmax = pixels.min(), pixels.max()
	return ( pmax - pmin ) / ( pmax + pmin )

def _MakeArrayIfPossible( x, *pargs, **kwargs ):
	return numpy.array( x, *pargs, **kwargs ) if numpy else x
	
def IdealToPhysicalLuminance( idealLuminance, physicalScreenRange ):
	"""
	Convert ideal luminance (from 0 to 1) to physical luminance.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    idealLuminance:
	        "ideal" luminance value(s) to convert (in the range 0 to 1)
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Physical luminance value(s) corresponding to the ideal input
		value(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return screenPhysicalMin + ( screenPhysicalMax - screenPhysicalMin ) * _MakeArrayIfPossible( idealLuminance )

def PhysicalToIdealLuminance( physicalLuminance, physicalScreenRange ):
	"""
	Convert physical luminance to ideal luminance (from 0 to 1).
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    physicalLuminance:
	        physical luminance value(s) to convert
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Ideal luminance value(s) (in the range 0 to 1) corresponding to
		the physical input value(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return ( _MakeArrayIfPossible( physicalLuminance ) - screenPhysicalMin ) / ( screenPhysicalMax - screenPhysicalMin )

def IdealToPhysicalContrastRatio( idealContrastRatio, idealBackgroundLuminance, physicalScreenRange ):
	"""
	Convert one or more ideal contrast ratios to physical contrast ratios.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    idealContrastRatio:
	        "ideal" contrast ratio(s) to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Physical contrast ratio(s) corresponding to the ideal input
		value(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return _MakeArrayIfPossible( idealContrastRatio ) * idealBackgroundLuminance / ( idealBackgroundLuminance + screenPhysicalMin / float( screenPhysicalMax - screenPhysicalMin ) )

def PhysicalToIdealContrastRatio( physicalContrast, idealBackgroundLuminance, physicalScreenRange ):
	"""
	Convert one or more physical contrast ratios to ideal contrast ratios.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    physicalContrastRatio:
	        physical contrast ratio(s) to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Ideal contrast ratio(s) corresponding to the physical input
		ratio(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return _MakeArrayIfPossible( physicalContrast ) / float( idealBackgroundLuminance ) * ( idealBackgroundLuminance + screenPhysicalMin / float( screenPhysicalMax - screenPhysicalMin ) )

def IdealContrastRatioToNormalizedContrast( idealContrastRatio, idealBackgroundLuminance ):
	"""
	Convert one or more ideal contrast ratios to normalized contrast scaling
	factors. For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    idealContrastRatio:
	        "ideal" contrast ratio(s) to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	Returns:
		Normalized contrast scaling factors(s) corresponding to the input
		ideal contrast ratio(s).
	"""
	return 2.0 * idealBackgroundLuminance * idealContrastRatio

def NormalizedContrastToIdealContrastRatio( normalizedContrast, idealBackgroundLuminance ):
	"""
	Convert one or more normalized contrast values to ideal contrast ratios.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    normalizedContrast:
	        normalized contrast scaling factor(s) (in the range 0 to 1)
	        to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	Returns:
		Ideal contrast ratio(s) corresponding to the input normalized
		contrast scaling factor(s).
	"""
	return 0.5 * normalizedContrast / float( idealBackgroundLuminance )

def ContrastTest( normalizedContrast=1.0, idealBackgroundLuminance=0.5, physicalScreenRange=( 10.1, 221 ) ):
	idealLuminances = numpy.array( [ -1.0, +1.0, -1.0, +1.0, -1.0, +1.0 ] ) * 0.5 * normalizedContrast + idealBackgroundLuminance
	physicalLuminances = IdealToPhysicalLuminance( idealLuminances, physicalScreenRange )
	physicalBackgroundLuminance = IdealToPhysicalLuminance( idealBackgroundLuminance, physicalScreenRange )
	idealBackgroundLuminance_recon = PhysicalToIdealLuminance( physicalBackgroundLuminance, physicalScreenRange )
	
	def Report( name, value, reconstruction ):
		print( '%30s = %6f    (reconstructed value = %6f; error = %+g)' % ( name, value, reconstruction, reconstruction - value ) )
		
	Report( 'idealBackgroundLuminance', idealBackgroundLuminance, idealBackgroundLuminance_recon )
	idealRMSContrastRatio = RMSContrastRatio( idealLuminances, idealBackgroundLuminance )
	physicalRMSContrastRatio = RMSContrastRatio( physicalLuminances, physicalBackgroundLuminance )
	idealRMSContrastRatio_recon = PhysicalToIdealContrastRatio( physicalRMSContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	physicalRMSContrastRatio_recon = IdealToPhysicalContrastRatio( idealRMSContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	Report( 'idealRMSContrastRatio', idealRMSContrastRatio, idealRMSContrastRatio_recon )
	Report( 'physicalRMSContrastRatio', physicalRMSContrastRatio, physicalRMSContrastRatio_recon )
	idealMichelsonContrastRatio = MichelsonContrastRatio( idealLuminances, idealBackgroundLuminance )
	physicalMichelsonContrastRatio = MichelsonContrastRatio( physicalLuminances, idealBackgroundLuminance )
	idealMichelsonContrastRatio_recon = PhysicalToIdealContrastRatio( physicalMichelsonContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	physicalMichelsonContrastRatio_recon = IdealToPhysicalContrastRatio( idealMichelsonContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	Report( 'idealMichelsonContrastRatio', idealMichelsonContrastRatio, idealMichelsonContrastRatio_recon )
	Report( 'physicalMichelsonContrastRatio', physicalMichelsonContrastRatio, physicalMichelsonContrastRatio_recon )

	
