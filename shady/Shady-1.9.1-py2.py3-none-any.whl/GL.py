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
import sys
import math
import ctypes
import threading

from . import DependencyManagement

# The point of this module is to import OpenGL bindings, either from pyglet (preferred, but more laborious) or from PyOpenGL
pyglet = OpenGL = original = None

# home-made 'six'-esque stuff:
basestring = ( unicode, bytes ) = ( unicode, str ) if sys.version < '3' else ( str, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x

def Unimport(): return False

if original is None:
	try: import OpenGL, OpenGL.GL as original
	except ImportError: pass
if original is None:
	try: import pyglet, pyglet.gl as original  # this line has the side effect of creating pyglet's "shadow context" and hence commits you to doing all gl* calls in this thread
	except ImportError: pass

if pyglet:
	from pyglet.gl import *
	DependencyManagement.RegisterVersion( name='pyglet', value=pyglet.version )
	
	# do the ctypes wrapping that PyOpenGL would otherwise have done for us
	def intwrap( func, return_type=GLuint ):
		def wrapped( *pargs ):
			result = return_type()
			pargs = pargs + ( ctypes.byref( result ), )
			func( *pargs )
			return result.value
		return wrapped
	def wrap_array_output( func, return_type=GLuint ):
		def wrapped( *pargs ):
			n = pargs[ -1 ]
			array = ( return_type * n )()
			pargs = pargs + ( array, )
			func( *pargs )
			return array[ 0 ] if n == 1 else list( array )
		return wrapped
	def wrap_array_input( func, return_type=GLuint ):
		def wrapped( *pargs ):
			n = pargs[ -2 ]
			array = pargs[ -1 ]
			array = ( return_type * n )( *array )
			pargs = pargs[ :-1 ] + ( array, )
			func( *pargs )
			return array[ 0 ] if n == 1 else list( array )
		return wrapped
			
	glGetShaderiv = intwrap( original.glGetShaderiv, GLint  )
	glGetProgramiv = intwrap( original.glGetProgramiv, GLint  )
	glGetQueryObjectuiv = intwrap( original.glGetQueryObjectuiv, GLuint )
	glGetIntegerv = intwrap( original.glGetIntegerv, GLint )
	glGenTextures = wrap_array_output( original.glGenTextures, GLuint )
	glGenQueries  = wrap_array_output( original.glGenQueries,  GLuint )
	glGenBuffers  = wrap_array_output( original.glGenBuffers,  GLuint )
	glDeleteBuffers = wrap_array_input( original.glDeleteBuffers, GLuint )
	
	def glShaderSource( shader, source ):
		try: source = [ c.encode( 'utf-8' ) for c in source ]
		except: pass
		count = len( source )
		src = ( ctypes.c_char_p * count )( *source )
		return original.glShaderSource( shader, count, ctypes.cast( ctypes.pointer( src ), ctypes.POINTER( ctypes.POINTER( ctypes.c_char ) ) ), None )
	def glGetShaderInfoLog( shader ):
		size = glGetShaderiv(shader, original.GL_INFO_LOG_LENGTH ) # NB: using wrapped version of glGetShaderiv defined above; for some reason GL_INFO_LOG_LENGTH is defined in, but not exported by, pyglet.gl
		buffer = ctypes.create_string_buffer( size )
		original.glGetShaderInfoLog( shader, size, None, buffer )
		return IfStringThenNormalString( buffer.value )
	def glGetProgramInfoLog( program ):
		size = glGetProgramiv( program, original.GL_INFO_LOG_LENGTH ) # NB: using wrapped version of glGetProgramiv defined above; for some reason GL_INFO_LOG_LENGTH is defined in, but not exported by, pyglet.gl
		buffer = ctypes.create_string_buffer( size )
		original.glGetProgramInfoLog( program, size, None, buffer )
		return IfStringThenNormalString( buffer.value )
	def glGetString( name ):
		return IfStringThenNormalString( ctypes.cast( original.glGetString( name ), ctypes.c_char_p ).value )
	def glReadPixels( x, y, w, h, format, type ):
		if format == GL_RGB: bytesPerPixel = 3
		elif format == GL_RGBA: bytesPerPixel = 4
		else: raise TypeError( 'TODO: wrapped version of glReadPixels cannot yet support formats other than GL_RGB/GL_RGBA' )
		if type != GL_UNSIGNED_BYTE: raise TypeError( 'TODO: wrapped version of glReadPixels cannot yet support data types other than GL_UNSIGNED_BYTE' )
		buf = ( ctypes.c_uint8 * w * h * bytesPerPixel )()
		original.glReadPixels( x, y, w, h, format, type, buf )
		return buf
	def glGetUniformLocation( program, varName ):
		return original.glGetUniformLocation( program, IfStringThenRawString( varName ) )
	
	gl_import_thread = threading.current_thread()
	
	def Unimport():
		DependencyManagement.Unimport( 'pyglet' )
		return True
		
	#def UseVBL( value=1 ):
	#	failmsg = 'UseVBL(%r) failed' % value
	#	if sys.platform.lower().startswith( 'win' ):
	#		from pyglet.gl.wglext_arb import wglSwapIntervalEXT
	#		try: return wglSwapIntervalEXT( value )
	#		except Exception as e: failmsg += ': ' + str( e )
	#	print( failmsg )
	
elif OpenGL:
	from OpenGL.GL import *
	DependencyManagement.RegisterVersion( name='pyopengl', value=OpenGL.__version__ )
	try: GL_TIME_ELAPSED
	except NameError: GL_TIME_ELAPSED = 35007 # defined in PyOpenGL 3.1 but not 3.0 (but works anyway if defined here by hand)
	gl_import_thread = None
	#def UseVBL( value=1 ):
	#	failmsg = 'UseVBL(%r) failed' % value
	#	if sys.platform.lower().startswith( 'win' ):
	#		from OpenGL.WGL import wglSwapIntervalEXT
	#		try: return wglSwapIntervalEXT( value )
	#		except Exception as e: failmsg += ': ' + str( e )
	#	print( failmsg )
	def glGetShaderInfoLog( shader ): return IfStringThenNormalString( original.glGetShaderInfoLog( shader ) )
	def glGetProgramInfoLog( program ): return IfStringThenNormalString( original.glGetProgramInfoLog( program ) )
	def glGetString( name ): return IfStringThenNormalString( original.glGetString( name ) )
else:
	raise ImportError( 'failed to import either pyglet or OpenGL' )

DependencyManagement.RegisterVersion( name='OpenGL', value=glGetString( GL_VERSION ) )
DependencyManagement.RegisterVersion( name='GLSL',   value=glGetString( GL_SHADING_LANGUAGE_VERSION ) )


def glGetDACPrecision( legacy=True ):
	if legacy:
		# old way (compatibility profiles):
		return glGetIntegerv( GL_RED_BITS )
	else:
		# MODERNGLTODO here's a new way for OpenGL 3+, based on https://stackoverflow.com/a/15137195/ but may be buggy with some drivers
		glBindFramebuffer( GL_FRAMEBUFFER, 0 );
		bits = GLint()
		glGetFramebufferAttachmentParameteriv( GL_FRAMEBUFFER, GL_FRONT_LEFT, GL_FRAMEBUFFER_ATTACHMENT_RED_SIZE, ctypes.byref( bits ) );
		return bits.value


def glUniformTextureSlot( address, val ):
	if val >= 0:
		glUniform1i( address, val )
		glActiveTexture( val + GL_TEXTURE0 )

def glBindTexture_IfNotNegative( val ):
	if val >= 0: glBindTexture( GL_TEXTURE_2D, val )
	
def glUniformTransformation3( address, *vals ):
	glUniformMatrix3fv( address, 1, GL_TRUE, ( ctypes.c_float * 9 )( *vals[ : 9 ] ) )

def glUniformTransformation4( address, *vals ):
	glUniformMatrix4fv( address, 1, GL_TRUE, ( ctypes.c_float * 16 )( *vals[ : 16 ] ) )

def glCallList_IfNotNegative( val ):
	if val >= 0: glCallList( val )

def glClearColor_RGB( r, g, b ):
	glClearColor( r, g, b, 0.0 )

