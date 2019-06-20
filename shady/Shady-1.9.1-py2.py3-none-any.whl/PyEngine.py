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
This module contains alternative implementations, in Python, of the
under-the-hood rendering procedures that are replicated in the C++
source code of the ShaDyLib accelerator. The PyEngine is used only
when the accelerator is absent, or when the accelerator is explicitly
disabled before `World` creation, e.g. with::

	Shady.BackEnd( 'pyglet', acceleration=False )

Falling back to the PyEngine, rather than the binary accelerator,
would allow Shady to be "pure" Python, although it then becomes
dependent on additional third-party packages for wrapping the
windowing setup (one option is `pyglet`) and also for wrapping the
OpenGL calls required for rendering (`pyglet`, or `OpenGL` from the
pyopengl project).

The PyEngine has major disadvantages for timing performance: in our
experience (mostly on Windows 10 Pro and Windows 10 Home) it will
perform well some of the time, indistinguishable from the accelerator,
but then at random uncontrollable times the operating system will
interrupt the Python interpreter and cause glitches. These glitches
go away, or become very rare, if you use the accelerator.
"""

# NB---Accelerator functions that the PyEngine does not replicate:
# - WaitForNextFrame() (pyglet already seems to grok this well)
# - GetUpdatedKeys()   (don't even try---too slow in Python)
# - Accounting for .perspectiveCameraAngle in _ComputeWorldProjection()
#   (TODO: that's a method, defined in Rendering, but like many such
#   methods that have been overshadowed by accelerated implementations,
#   it really should be moved here.)

import os
import re
import sys
import math
import ctypes
import itertools
try:                from itertools import islice, zip_longest  # Python 3
except ImportError: from itertools import islice, izip_longest as zip_longest  # Python 2

from . import Dependencies; from .Dependencies import numpy
from . import Timing

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )

class NotYetImported( object ):
	def __init__( self, name ): self.__name = name
	def __getattr__( self, name ): raise RuntimeError( "thread-sensitive module %s has not yet been imported" % self.__name )
	def Unimport( self ): return False

GL = NotYetImported( 'GL' )

def EnableGL():
	global GL
	from . import GL
	return GL
	
def CleanUpGL():
	global GL
	if GL.Unimport():
		sys.modules.pop( GL.__name__, None )
		GL = NotYetImported( 'GL' )
	
def InitShading( glslDirectory, substitutions ):
	# accelerated
	EnableGL()
	glslVersion = GL.glGetString( GL.GL_SHADING_LANGUAGE_VERSION )
	modes = ""
	if glslVersion >= '3.3': modes += " MODERN"
	versionHeaderSource  = os.path.join( glslDirectory, 'Version.glsl' )
	vertexShaderSource   = os.path.join( glslDirectory, 'VertexShader.glsl' )
	randomNumberSource   = os.path.join( glslDirectory, 'RandomGLSL330AndUp.glsl' if glslVersion >= '3.3' else 'Random.glsl' )
	fragmentShaderSource = os.path.join( glslDirectory, 'FragmentShader.glsl' )
	vertexShader   = CompileShader( GL.GL_VERTEX_SHADER,   modes, versionHeaderSource, vertexShaderSource, substitutions )
	fragmentShader = CompileShader( GL.GL_FRAGMENT_SHADER, modes, versionHeaderSource, randomNumberSource, fragmentShaderSource, substitutions )
	# build shader program
	program = GL.glCreateProgram()
	GL.glAttachShader( program, vertexShader   )
	GL.glAttachShader( program, fragmentShader )
	GL.glLinkProgram( program )
	# try to activate/enable shader program, handling errors wisely
	try: GL.glUseProgram( program )
	except: print( GL.glGetProgramInfoLog( program ) ); raise

	# enable alpha blending
	GL.glTexEnvf( GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE )
	#GL.glEnable( GL.GL_DEPTH_TEST ) # disabled by default but can be turned on via world.DepthTesting( True )
	#GL.glDepthFunc( GL.GL_LEQUAL ) # Nope, in fact don't do this
	GL.glEnable( GL.GL_BLEND )
	GL.glBlendEquation( GL.GL_FUNC_ADD )
	GL.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA )
	
	GL.glPixelStorei( GL.GL_PACK_ALIGNMENT, 1 )
	GL.glPixelStorei( GL.GL_UNPACK_ALIGNMENT, 1 )
	GL.glPixelStorei( GL.GL_PACK_SKIP_ROWS, 0 )
	GL.glPixelStorei( GL.GL_UNPACK_SKIP_ROWS, 0 )
	GL.glPixelStorei( GL.GL_PACK_SKIP_PIXELS, 0 )
	GL.glPixelStorei( GL.GL_UNPACK_SKIP_PIXELS, 0 )
	# should perhaps first save (and later restore?) these state with GL.glPushClientAttrib(GL.GL_CLIENT_PIXEL_STORE_BIT) and GL.glPopClientAttrib(GL.GL_CLIENT_PIXEL_STORE_BIT)
	# see https://www.opengl.org/archives/resources/features/KilgardTechniques/oglpitfall/
	
	return program

def EnableCulling( alphaThreshold ):
	GL.glEnable( GL.GL_DEPTH_TEST )
	if alphaThreshold >= 0.0:
		GL.glEnable( GL.GL_ALPHA_TEST )
		GL.glAlphaFunc( GL.GL_GREATER, alphaThreshold )
	else:
		GL.glDisable( GL.GL_ALPHA_TEST )
	
def DisableCulling():
	GL.glDisable( GL.GL_DEPTH_TEST )
	GL.glDisable( GL.GL_ALPHA_TEST )

def DisableShadyPipeline():
	GL.glUseProgram( 0 )

def QueryDACMax( legacy ):
	return 2.0 ** GL.glGetDACPrecision( legacy=legacy ) - 1.0


def CompileShader( type, modes, *sources ):
	# accelerated
	accumulatedSource = ''
	substitutions = {}
	for source in sources:
		if isinstance( source, basestring ):
			if not source.strip():
				continue
			token = '//#'
			if source.startswith( token ):
				for pair in re.split( r'\n\s*' + token, '\n' + source.strip() )[ 1: ]:
					search, replace = pair.split( None, 1 )
					substitutions[ token + search ] = replace.strip() + '\n' + token + search
				continue
			if '\n' not in source:
				lastFileName = source
				source = open( source, 'rt' )
		if hasattr( source, 'read' ):
			source = source.read()
		accumulatedSource += '\n' + source
	for search, replace in substitutions.items(): accumulatedSource = accumulatedSource.replace( search, replace )
	#for search, replace in substitutions.items(): print( 'search for %r and replace with %r\n\n' % ( search, replace ) )
	#open( lastFileName + '.accumulated', 'wt' ).write( accumulatedSource )
	for mode in re.split( r'[\+,;\|\s]+', modes.strip() ):
		if mode: accumulatedSource = accumulatedSource.replace( '//@' + mode + ' ', '' )
	shader = GL.glCreateShader( type )
	GL.glShaderSource( shader, accumulatedSource )
	GL.glCompileShader( shader )
	result = GL.glGetShaderiv( shader, GL.GL_COMPILE_STATUS )
	if result != 1: raise Exception( "Shader compilation failed:\n" + GL.glGetShaderInfoLog( shader ) )
	return shader

def SetUpProperties( instance, world=None, proplist=None ):
	# accelerated
	
	if world is None: world = instance
	if proplist is None: proplist = instance.Properties( False )
	
	for prop in proplist: prop.__get__( instance, type( instance ) ) # fills instance-specific value from the current default (important to do this now while the instance is being initialized)
	
	instance._property_transfers = transfers = []
	for prop in proplist:
		transferFunction = prop.transfer
		if transferFunction is not None:
			if callable( transferFunction ):
				transferFunctionName = transferFunction.__name__
			else:
				transferFunctionName = transferFunction
				if transferFunctionName.startswith( 'self.' ): transferFunction = getattr( instance, transferFunctionName[ 5: ] )
				else: transferFunction = getattr( GL, transferFunctionName )
			if transferFunctionName.split( '.' )[ -1 ].strip( '_' ).startswith( 'glUniform' ):
				uniformVariableName = 'u' + prop.name[ 0 ].upper() + prop.name[ 1: ]
				uniformVariableAddress = GL.glGetUniformLocation( world._program, uniformVariableName )
				if uniformVariableAddress < 0 and not prop.custom:
					raise NameError( 'failed to find a uniform shader variable called %r' % uniformVariableName )
			else:
				uniformVariableName = None
				uniformVariableAddress = None
			wrappedTransferFunction = WrapTransferFunction( transferFunction, instance._property_storage, prop.name, uniformVariableAddress, transferFunctionName )
			wrappedTransferFunction.prop = [ prop ]
			wrappedTransferFunction.functionName = transferFunctionName
			wrappedTransferFunction.uniformVariableName = uniformVariableName
			wrappedTransferFunction.uniformVariableAddress = uniformVariableAddress
			wrappedTransferFunction.enabled = True
			transfers.append( wrappedTransferFunction )
				
def WrapTransferFunction( transferFunction, container, key, uniformVariableAddress, transferFunctionName ):
	# accelerated
	# NB: we are baking `container[key]` rather than a fixed reference to an array, so that we can allow sharing/unsharing of properties
	if uniformVariableAddress is None:
		def wrappedTransferFunction( *pargs ):
			array = container[ key ]
			if pargs: array.flat = pargs # NB: .flat is numpy-specific
			transferFunction( *array )
	else:
		def wrappedTransferFunction( *pargs ):
			array = container[ key ]
			if pargs:
				try: array.flat = pargs # NB: .flat is numpy-specific
				except: array[ : ] = pargs
			transferFunction( uniformVariableAddress, *array )
	return wrappedTransferFunction
	
def EnableTransfer( instance, *propertyNames ):
	# not accelerated, but not really used anyway
	propertyNames = [ name for arg in propertyNames for name in arg.split() ]
	for transferFunction in instance._property_transfers:
		if transferFunction.prop[ 0 ].name in propertyNames: transferFunction.enabled = True

def DisableTransfer( instance, *propertyNames ):
	# not accelerated, but not really used anyway
	propertyNames = [ name for arg in propertyNames for name in arg.split() ]
	for transferFunction in instance._property_transfers:
		if transferFunction.prop[ 0 ].name in propertyNames: transferFunction.enabled = False

def ExecuteTransfers( instance ):
	# accelerated
	verbose = instance._verbose
	if verbose:
		print( '\n' + instance._Description() )
		instance._verbose -= 1
	for transferFunction in instance._property_transfers:
		if verbose:
			if transferFunction.enabled: print( '%s: %s(%s)' % ( transferFunction.prop[ 0 ].name, transferFunction.functionName, ', '.join( str( x ) for x in transferFunction.prop[ 0 ].determine_array( instance ) ) ) )
			else: print( transferFunction.prop[ 0 ].name + ': DISABLED' )
		if transferFunction.enabled: transferFunction()

def DrawWorld( world, dt=None, t=None ):
	# dt is passed (as sole argument) by PygletWindowing when auto=True, but we will not use it
	# TODO: in PygletWindowing with auto=True, call time is delayed by the time it took to process mouse events, etc...
	if t is None: t = Timing.Seconds() # call time
	world._drawTime = t
	db = world.debugTiming
	firstFrame = ( world.framesCompleted == 0 )
	world._SortStimuli(); db and world._DebugTiming( 'Separated' )
	GL.glUseProgram( world._program )
	if firstFrame:
		GL.glClearColor( 0.0, 0.0, 0.0, 0.0 )
		GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )
	else:
		world.shady = 1
		ExecuteTransfers( world )  # Send world uniforms to GPU (last one, `drawMode`, also triggers draw method).
		db and world._DebugTiming( 'Transfer' )
		GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )  # Depth buffer clear does nothing if not enabled
		db and world._DebugTiming( 'glClear' )
		drawOrder = world._shady_stimuli
		if GL.glIsEnabled( GL.GL_DEPTH_TEST ): drawOrder = drawOrder[ ::-1 ]
		for stimulus in drawOrder:
			if stimulus._accel: stimulus._accel.Draw(); continue  # now that ShaDyLib accelerates World objects (under the name Renderer) as well as Stimulus objects, this will not happen
			if not stimulus.visible: continue
			if stimulus.textureSlotNumber < 0: stimulus.useTexture = False
			ExecuteTransfers( stimulus )
		db and world._DebugTiming( 'DrawStimuli' )
		GL.glBindTexture( GL.GL_TEXTURE_2D, 0 ) # required to support foreign stimuli
		db and world._DebugTiming( 'UnbindTexture' )
	world._FrameCallback( t )
	world.framesCompleted += 1
		
def WaitForGPU():
	# not yet accelerated
	GL.glFinish()
	
def CaptureRawRGBA( size, origin=None ):
	# accelerated 
	EnableGL()
	return GL.glReadPixels( origin[ 0 ], origin[ 1 ], size[ 0 ], size[ 1 ], GL.GL_RGBA, GL.GL_UNSIGNED_BYTE )

def CaptureToTexture( destTextureID, size, origin=None ):
	# accelerated 
	EnableGL()
	if origin is None: origin = ( 0, 0 )
	if not destTextureID or destTextureID < 0: raise ValueError( 'destination texture has not been assigned' )
	#if not destTextureID or destTextureID < 0: destTextureID = GL.glGenTextures( 1 ) # NB: also need to reserve a slot number for glActivateTexture
	GL.glBindTexture( GL.GL_TEXTURE_2D, destTextureID )
	GL.glCopyTexImage2D( GL.GL_TEXTURE_2D, 0,   GL.GL_RGB32F,    origin[ 0 ], origin[ 1 ],   size[ 0 ], size[ 1 ],  0 )
	GL.glBindTexture( GL.GL_TEXTURE_2D, 0 )
	return destTextureID

def GetNumberOfTextureSlots():
	# accelerated (as Renderer method, for convenience of access, although in principle it could be a global function)
	return GL.glGetIntegerv( GL.GL_MAX_TEXTURE_IMAGE_UNITS ) # this returns the number available for fragment-shader use although additional units may be usable by the vertex shader

def CtypeArray( values, c_type, nElements=None ):
	if nElements is None: nElements = len( values )
	return ( c_type * nElements )( *values )

def UpdateModernBuffers( stim, vertices, indices=None, nBy2=True, addHalf=False ):
	isCtypesArray = isinstance( vertices, ctypes.Array )
	nPoints = stim.nPoints
	if nBy2:
		nCoords2D = nPoints * 2
		nCoords3D = nPoints * 3
		if not numpy or isCtypesArray:
			vertices = CtypeArray( [], GL.GLfloat, nCoords3D )
			if addHalf:
				vertices[ 0::3 ] = [ x + 0.5 for x in vIn[ 0:nCoords2D:2 ] ]
				vertices[ 1::3 ] = [ y + 0.5 for y in vIn[ 1:nCoords2D:2 ] ]
			else:
				vertices[ 0::3 ] = vIn[ 0:nCoords2D:2 ]
				vertices[ 1::3 ] = vIn[ 1:nCoords2D:2 ]
			
		else: # assume n-by-2 numpy array, or otherwise a sequence of n sequences each of length 2
			vertices = numpy.c_[ vertices, numpy.zeros( nPoints ) ]
			if addHalf: vertices[ :, :2 ] += 0.5
			vertices = CtypeArray( vertices.flat, GL.GLfloat, nCoords3D )
	elif not isCtypesArray:
		# assume a flat list, already 3 coordinates per vertex, already truncated to correct length
		if addHalf: raise NotImplementedError( 'this should not happen' )
		vertices = CtypeArray( vertices, GL.GLfloat )
	
	if stim._vbo is None: stim._vbo = GL.glGenBuffers( 1 )
	GL.glBindBuffer( GL.GL_ARRAY_BUFFER, stim._vbo )
	if stim._vao is None: stim._vao = GL.glGenVertexArrays( 1 )
	GL.glBindVertexArray( stim._vao )
	if stim._ebo is None: stim._ebo = GL.glGenBuffers( 1 )
	GL.glBindBuffer( GL.GL_ELEMENT_ARRAY_BUFFER, stim._ebo )
	
	if len( vertices ) > stim._vboAllocatedLength:
		GL.glBufferData( GL.GL_ARRAY_BUFFER, ctypes.sizeof( vertices ), vertices, GL.GL_STATIC_DRAW ) # TODO: is STATIC_DRAW the best?
		stim._vboAllocatedLength = len( vertices )
		#print('vertices = %r\n' % list( vertices ) )
		
		GL.glVertexAttribPointer( 0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None )
		GL.glEnableVertexAttribArray( 0 )
	else:
		GL.glBufferSubData( GL.GL_ARRAY_BUFFER, 0, ctypes.sizeof( vertices ), vertices )
		
	if indices is not None:
		indices  = CtypeArray( indices, GL.GLint )
		if len( indices ) > stim._eboAllocatedLength:
			GL.glBufferData( GL.GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof( indices ), indices, GL.GL_STATIC_DRAW )
			stim._eboAllocatedLength = len( indices )
			#print('indices  = %r\n' % list( indices ) )
		else:
			GL.glBufferSubData( GL.GL_ELEMENT_ARRAY_BUFFER, 0, ctypes.sizeof( indices ), indices )
		

def InitQuad( stim, legacy=True ):
	stim._legacy = legacy
	if not legacy:
		stim._vao = None
		stim._vbo = None
		stim._ebo = None
		stim._vboAllocatedLength = 0
		stim._eboAllocatedLength = 0
		stim._previousQuadSize = None
		DrawModernQuad( stim, phantom=True )
	
def DrawModernQuad( stim, phantom=False ):
	w, h = stim.envelopeSize
	if stim._previousQuadSize != ( w, h ):
		stim._previousQuadSize = ( w, h )
		UpdateModernBuffers( stim, vertices=( 0,0,0,  w,0,0,  w,h,0,  0,h,0 ), indices=( 0, 1, 2, 0, 2, 3 ), nBy2=False )
	else:
		GL.glBindVertexArray( stim._vao )
	if not phantom:
		GL.glDrawElements( GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None )

def DrawModernPoints( stim ):
	stim._previousQuadSize = None
	UpdateModernBuffers( stim, stim.points, nBy2=True, addHalf=True )
	GL.glDrawArrays( GL.GL_POINTS, 0, stim.nPoints )
	
def DrawModernLines( stim, strip=False, loop=False ):
	stim._previousQuadSize = None	
	indices = []
	xy, nCoords = stim.points, stim.nPoints * 2
	try: x, y = xy[ :, 0 ], xy[ :, 1 ]
	except: x, y = islice( xy, 0, nCoords, 2 ), islice( xy, 1, nCoords, 2 )
	root = prev = None
	for i, ( xi, yi ) in enumerate( zip_longest( x, y ) ):
		if math.isnan( xi ) or math.isnan( yi ):
			if loop and prev is not None and root is not None: indices += ( prev, root )
			root = prev = None
			continue
		if root is None: root = i
		if prev is None: prev = i   # yes, DrawModernLines has an if here, whereas DrawModernPolygons has an elif
		else: indices += ( prev, i ); prev = i if strip else None
	if loop and prev is not None and root is not None: indices += ( prev, root )
	UpdateModernBuffers(stim, xy, indices, nBy2=True, addHalf=True )
	GL.glDrawElements( GL.GL_LINES, len( indices ), GL.GL_UNSIGNED_INT, None )

def DrawModernPolygons( stim ):
	stim._previousQuadSize = None	
	indices = []
	xy, nCoords = stim.points, stim.nPoints * 2
	try: x, y = xy[ :, 0 ], xy[ :, 1 ]
	except: x, y = islice( xy, 0, nCoords, 2 ), islice( xy, 1, nCoords, 2 )
	root = prev = None
	for i, ( xi, yi ) in enumerate( zip_longest( x, y ) ):
		if math.isnan( xi ) or math.isnan( yi ): root = prev = None; continue
		if   root is None: root = i
		elif prev is None: prev = i   # yes, DrawModernLines has an if here, whereas DrawModernPolygons has an elif
		else: indices += ( root, prev, i ); prev = i
	UpdateModernBuffers(stim, xy, indices, nBy2=True )
	GL.glDrawElements( GL.GL_TRIANGLES, len( indices ), GL.GL_UNSIGNED_INT, None )

def DrawShapes( mode, stim ):
	""" Issue actual draw commands to OpenGL for simple envelope quad, or another draw type. """
	modeName, drawType, smoothingType, penThicknessFunction = mode
	if drawType is None:
		if   modeName == 'QUAD':       mode[ 1: ] = drawType, smoothingType, penThicknessFunction = GL.GL_QUADS,      None,                 None
		elif modeName == 'POINTS':     mode[ 1: ] = drawType, smoothingType, penThicknessFunction = GL.GL_POINTS,     GL.GL_POINT_SMOOTH,   GL.glPointSize
		elif modeName == 'LINES':      mode[ 1: ] = drawType, smoothingType, penThicknessFunction = GL.GL_LINES,      GL.GL_LINE_SMOOTH,    GL.glLineWidth
		elif modeName == 'LINE_STRIP': mode[ 1: ] = drawType, smoothingType, penThicknessFunction = GL.GL_LINE_STRIP, GL.GL_LINE_SMOOTH,    GL.glLineWidth
		elif modeName == 'POLYGON':    mode[ 1: ] = drawType, smoothingType, penThicknessFunction = GL.GL_POLYGON,    GL.GL_POLYGON_SMOOTH, None
		elif modeName == 'LINE_LOOP':  mode[ 1: ] = drawType, smoothingType, penThicknessFunction = GL.GL_LINE_LOOP,  GL.GL_LINE_SMOOTH,    GL.glLineWidth
	smoothing = stim.smoothing
	filled = modeName in ( 'QUAD', 'POLYGON' )
	
	if smoothing <= 1 and filled: # this is so that we can avoid the often-buggy
		smoothing = 0 # GL_POLYGON_SMOOTH mode by default, but still force it on if we set .smoothing > 1  
	if smoothingType:
		if smoothing: GL.glEnable(  smoothingType )
		else:         GL.glDisable( smoothingType )
	if penThicknessFunction:
		penThicknessFunction( stim.penThickness )
	
	if stim._legacy:
		# Legacy OpenGL (immediate mode).
		if modeName == 'QUAD':
			w, h = stim.envelopeSize
			GL.glBegin( drawType )
			GL.glVertex3f( 0.0, 0.0, 0.0 )
			GL.glVertex3f( w,   0.0, 0.0 )
			GL.glVertex3f( w,   h,   0.0 )
			GL.glVertex3f( 0.0, h,   0.0 )
			GL.glEnd()
		elif stim.nPoints:
			xy, nCoords = stim.points, stim.nPoints * 2
			try: x, y = xy[ :, 0 ], xy[ :, 1 ]
			except: x, y = islice( xy, 0, nCoords, 2 ), islice( xy, 1, nCoords, 2 )
			GL.glBegin( drawType )
			for xi, yi in zip_longest( x, y ):
				if math.isnan( xi ) or math.isnan( yi ): GL.glEnd(); GL.glBegin( drawType )
				else:
					if not filled: xi += 0.5; yi += 0.5
					GL.glVertex3f( xi, yi, 0.0 )
			GL.glEnd()
			
	else:
		# Modern OpenGL
		if modeName == 'QUAD':
			DrawModernQuad( stim )
		elif stim.nPoints:
			if   modeName == 'POINTS':  DrawModernPoints( stim )
			elif modeName == 'POLYGON': DrawModernPolygons( stim )
			else: DrawModernLines( stim, strip=( modeName in ( 'LINE_STRIP', 'LINE_LOOP' ) ), loop=( modeName == 'LINE_LOOP' ) )

def LoadTexture( textureSlotNumber, textureID, width, height, nChannels, dataType, data, isLUT=False ):
	# accelerated
	internalFormatGL, formatGL, dtypeGL = DetermineFormats( nChannels, dataType )
	if textureID < 0: textureID = GL.glGenTextures( 1 )
	#previousActiveTextureUnit = GL.glGetIntegerv( GL.GL_ACTIVE_TEXTURE )
	textureUnitCode = GL.GL_TEXTURE0 + textureSlotNumber
	GL.glActiveTexture( textureUnitCode )
	#previousTextureID = GL.glGetIntegerv( GL.GL_TEXTURE_BINDING_2D )
	GL.glBindTexture( GL.GL_TEXTURE_2D, textureID )
	GL.glEnable( GL.GL_TEXTURE_2D )
	GL.glTexImage2D( GL.GL_TEXTURE_2D, 0, internalFormatGL, width, height, 0, formatGL, dtypeGL, data )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST       if isLUT else GL.GL_LINEAR )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST       if isLUT else GL.GL_LINEAR )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,     GL.GL_CLAMP_TO_EDGE if isLUT else GL.GL_REPEAT )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,     GL.GL_CLAMP_TO_EDGE if isLUT else GL.GL_REPEAT )
	GL.glBindTexture( GL.GL_TEXTURE_2D, 0 ) # required to support foreign stimuli
	return textureID

def SetLinearMagnification( textureID, setting ):
	if textureID <= 0: return setting
	GL.glBindTexture( GL.GL_TEXTURE_2D, textureID )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR if setting else GL.GL_NEAREST )
	GL.glBindTexture( GL.GL_TEXTURE_2D, 0 )
	return setting

def LoadSubTexture( textureSlotNumber, textureID, column, row, width, height, nChannels, dataType, data ):
	# accelerated
	internalFormatGL, formatGL, dtypeGL = DetermineFormats( nChannels, dataType )
	#previousActiveTextureUnit = GL.glGetIntegerv( GL.GL_ACTIVE_TEXTURE )
	textureUnitCode = GL.GL_TEXTURE0 + textureSlotNumber
	GL.glActiveTexture( textureUnitCode )
	#previousTextureID = GL.glGetIntegerv( GL.GL_TEXTURE_BINDING_2D )
	GL.glBindTexture( GL.GL_TEXTURE_2D, textureID )
	GL.glEnable( GL.GL_TEXTURE_2D )
	GL.glTexSubImage2D( GL.GL_TEXTURE_2D, 0, column, row, width, height, formatGL, dtypeGL, data )
	GL.glBindTexture( GL.GL_TEXTURE_2D, 0 ) # required to support foreign stimuli

		
def DetermineFormats( nChannels, dataType ):
	# accelerated
	if    dataType in [ 'uint8'   ]: floating = False; dtypeGL = GL.GL_UNSIGNED_BYTE
	elif  dataType in [ 'float32' ]: floating = True;  dtypeGL = GL.GL_FLOAT
	else: raise ValueError( "dataType must be 'float32' or 'uint8'" )

	FORMATS = dict( GL_R=8194, GL_R32F=33326, GL_R8=33321, GL_RED=6403, GL_RG=33319, GL_RG32F=33328, GL_RG8=33323, GL_RGB=6407, GL_RGB32F=34837, GL_RGB8=32849, GL_RGBA=6408, GL_RGBA32F=34836, GL_RGBA8=32856, )
	for k, v in FORMATS.items():
		if getattr( GL, k, None ) is None: setattr( GL, k, v )
	
	if    nChannels == 1: formatGL = GL.GL_RED;  internalFormatGL = GL.GL_R32F    if floating else GL.GL_R8
	elif  nChannels == 2: formatGL = GL.GL_RG;   internalFormatGL = GL.GL_RG32F   if floating else GL.GL_RG8
	elif  nChannels == 3: formatGL = GL.GL_RGB;  internalFormatGL = GL.GL_RGB32F  if floating else GL.GL_RGB8
	elif  nChannels == 4: formatGL = GL.GL_RGBA; internalFormatGL = GL.GL_RGBA32F if floating else GL.GL_RGBA8
	else: raise ValueError( "nChannels must be 1, 2, 3, or 4" )
	return internalFormatGL, formatGL, dtypeGL

class PropertyArray( object ):
	def __init__( self, propertyName, stimuli ):
		from . import Dependencies
		self.A = Dependencies.numpy.concatenate( [ getattr( stimulus, propertyName )[ None, : ] for stimulus in stimuli ], axis=0 )
