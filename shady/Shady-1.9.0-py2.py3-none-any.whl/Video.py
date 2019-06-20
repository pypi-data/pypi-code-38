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
This submodule is not imported by default by the parent package.
Import it for its side-effect: it enables the `.video` property
of the `Shady.Stimulus` class.

If `s` is a `Stimulus` instance and `s.video` is equal to its
default value of `None`, then saying::

    s.video = 'fish.mp4'

implicitly creates a `VideoSource` object with the `source`
property equal to `'fish.mp4'`.  (If `s.video` was previously
already a `VideoSource`, object then its `source` property is
simply updated accordingly.)

The third-party package `cv2` (installable with
`pip install opencv-python`) is required for video support.
Any source readable by `cv2.VideoCapture` is acceptable: 
use an integer to open a live camera stream, or a string to
specify a video file name.

If you want to record the video to disk while rendering, there
are two approaches. One way is to capture frames in a way that
is time- (or frame-) locked to the animation of  the `World`:
in this case, see the doc for the `VideoRecording` class, which
can capture the content of *any* `Stimulus` regardless of
whether its source is a `VideoSource`, or even capture an entire
`World`.  The other way is to record a `VideoSource` that is
already attached to a `Stimulus`, sub-sampling frames at an
independent pace in a background thread: in this case, simply
call `s.video.Record(filename)`.

If you want to record a video to disk *without* attaching it to
a `Shady.Stimulus`, or even without having a `Shady.World`
running at all. Let's say you want to record from camera 0::

    from Shady.Video import VideoSource
    s = VideoSource(0).Record('foo')
    # ...
    s.Close()

An acquisition thread will continually read frames from the
camera until you call `s.Close()`. A separate recording thread
will continually write frames to the specified file (`foo.avi`
in this example) until you call either `s.Close()` or
`s.StopRecording()`.

Note that reading frames from a camera or file, capturing
stimulus content into memory, and recording video frames to
disk all use RAM and place a burden on the CPU---they are
not intended for applications in which precise timing is
critical.
"""

__all__ = [
	'VideoSource',
]
import os
import sys
import time
import threading

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )

from . import Timing
from . import Utilities
from . import Rendering
from . import DependencyManagement

cv2 = DependencyManagement.Import( 'cv2', packageName='opencv-python', registerVersion=True )

DependencyManagement.Require( 'cv2', 'numpy' )

# home-made 'six'-esque stuff:
try: apply
except NameError: apply = lambda x: x()
try: FileNotFoundError
except NameError: FileNotFoundError = IOError


class VideoSource( Rendering.Scheduled ):
	
	stimulus = Rendering.Scheduled.parent
	
	def __init__( self, source=None, stimulus=None ):
		self.__handle = None
		self.__live = None
		self.__playing = False
		self.__newFrame = None
		self.__oldFrame = None
		self.__tprev = None
		self.__playhead = 0.0
		self.__jumpToTime = None
		self.__jumpToFrame = None
		self.__frameIndex = None
		self.__fps = None
		self.__frameCount = None
		self.__frameWidth = None
		self.__frameHeight = None
		self.__aperture_size = [ -1, -1 ]
		self.__aperture_offset = [ 0, 0 ]
		self.__loop = False
		self.__speed = 1.0
		self.__source = None
		self.__changed = True
		self.__frameQueue = None
		self.__acquisitionThread = None
		self.__set_aperture = False
		self._blank = [ [ [ 0.0 ] * 4 ] ]
		self.__recorder = None
		self.__recordingThread = None
		self.lastFrameAcquired = None
		self.stimulus = stimulus
		self.source = source
	
	def __del__( self ):
		self.Close()
	
	def Close( self ):
		handle = self.__handle
		recorder = self.__recorder
		
		self.StopRecording()
			
		self.CancelUpdate()
		
		self.__frameQueue = None # signal to stop self.__acquisitionThread
		
		if recorder and self.__recordingThread and not self.__recordingThread.isAlive():
			time.sleep( 0.2 )
			try: recorder.Close()
			except: pass

		self.__handle = None
		if handle and handle.isOpened():
			handle.release()
			
		#if self.__acquisitionThread: self.__acquisitionThread.join()
				
	def _Update( self ):
		if not self.world: return
		if not self.__set_aperture:
			self.aperture = -1, -1, 0, 0
			self.__set_aperture = True
		if self.__handle is None:
			self.__newFrame = None
		elif self.__live:
			if self.__playing:
				if self.__frameQueue is None: self._AcquireFrames()
				if self.__frameQueue:
					self.__newFrame = self.__frameQueue.pop( 0 )
					self.__changed = True
			else:
				self.__frameQueue = None
		else:
			t = self.world.t
			if not self.__playing:     dt = 0.0; self.__tprev = None
			elif self.__tprev is None: dt = 0.0; self.__tprev = t
			else: dt = t - self.__tprev
			if dt != 0.0 or self.__jumpToTime is not None or self.__jumpToFrame is not None:
				self.__tprev = t
				if self.__jumpToFrame is not None:
					frame = int( self.__jumpToFrame )
					self.__playhead = float( frame ) / self.__fps
					self.__jumpToFrame = self.__jumpToTime = None
				else:
					if self.__jumpToTime is not None:
						self.__playhead = self.__jumpToTime
						self.__jumpToFrame = self.__jumpToTime = None
					else:
						self.__playhead += dt * self.__speed
					frame = int( self.__playhead * self.__fps )
				if self.__loop:
					frame %= self.__frameCount
				else:
					if frame < 0: frame = 0; self.__playing = False
					if frame > self.__frameCount: frame = self.__frameCount; self.__playing = False
				
				if frame != self.__frameIndex:
					if self.__frameIndex is None: self.__frameIndex = -1
					nAhead = frame - self.__frameIndex
					if nAhead < 0 or nAhead > 10:
						self.__handle.set( getattr( cv2, 'CAP_PROP_POS_FRAMES', 1 ), frame )
						nAhead = 1
					for i in range( nAhead ):
						f, pixels = self.__handle.read()
						self.__newFrame = None if pixels is None else pixels[ :, :, ::-1 ]
					self.__frameIndex = frame
					self.__changed = True
		
		stimulus = self.stimulus
		
		pixels = self.__newFrame
		
		if pixels is not None:
			x, y = self.__aperture_offset
			aw, ah = self.__aperture_size
			fh, fw = pixels.shape[ :2 ]
			col = max( 0, min( fw - aw, ( fw - aw ) // 2 + x ) )
			row = max( 0, min( fh - ah, ( fh - ah ) // 2 - y ) )
			if ( aw, ah, col, row ) != ( fw, fh, 0, 0 ):
				self.__newFrame = pixels = pixels[ row : row + ah, col : col + aw, : ]
				
		if pixels is None: pixels = self.__oldFrame
		else: self.__oldFrame = pixels
		
		if self.Transform:
			if pixels is not None: pixels = self.Transform( pixels, self.__changed )
			if pixels is not None: self.__newFrame = pixels; self.__changed = True
		
		if self.__changed and stimulus is not None:
			pixels = self.__newFrame
			stimulus.LoadTexture( self._blank if pixels is None else pixels, pixels is not None and min( stimulus.size ) <= 1 )
			self.__newFrame = None
			self.__changed = False
			
	def Transform( self, pixelArray, pixelArrayHasChanged ):
		"""
		Overshadowable hook that allows you to transform the image before
		it is transferred as a texture to the graphics card.
		
		Return a new pixelArray if you want to transform the image on this
		frame. Return None if you do not want to make a change.
		
		`pixelArrayHasChanged` is a boolean that indicates whether this
		(untransformed) frame is different from the previous (untransformed)
		frame.
		
		Note that if you choose to return non-None when `pixelArrayHasChanged`
		is False, you'll be forcing the stimulus to LoadTexture() more often
		than it otherwise would, introducing further CPU costs (over and above
		the cost of performing the transformation itself).
		"""
		pass
		
	def Play( self, position=None, speed=None, loop=None, frame=None ):
		if loop     is not None: self.loop     = loop
		if speed    is not None: self.speed    = speed
		if position is not None: self.position = position
		if frame    is not None: self.frame    = frame
		self.__playing = True
		#return self # abandoned this because it tends to leave unwanted references to the VideoSource object hanging around in IPython prompts
	def Pause( self, position=None, speed=None, loop=None, frame=None ):
		if loop     is not None: self.loop     = loop
		if speed    is not None: self.speed    = speed
		if position is not None: self.position = position
		if frame    is not None: self.frame    = frame
		self.__playing = False
		#return self # abandoned this because it tends to leave unwanted references to the VideoSource object hanging around in IPython prompts
	@apply
	def playing():
		def fget( self ): return self.__playing
		def fset( self, value ): self.__playing = True if value else False
		return property( fget=fget, fset=fset )
	@apply
	def loop():
		def fget( self ): return self.__loop
		def fset( self, value ): self.__loop = True if value else False
		return property( fget=fget, fset=fset )
	@apply
	def speed():
		def fget( self ):
			return 1.0 if self.__live else self.__speed 
		def fset( self, value ):
			if not self.__live: self.__speed = float( value )
		return property( fget=fget, fset=fset )
	
	fps      = property( lambda self: self.__fps )
	width    = property( lambda self: self.__frameWidth )
	height   = property( lambda self: self.__frameHeight )
	size     = property( lambda self: ( self.__frameWidth, self.__frameHeight ) )
	live     = property( lambda self: self.__live )
	duration = property( lambda self: None if self.__live or not self.__handle or not self.__fps else self.__frameCount / self.__fps )
	nFrames  = property( lambda self: None if self.__live or not self.__handle else self.__frameCount )
	
	@apply
	def aperture():
		def fget( self ):
			stimulus = self.stimulus
			if stimulus is None: return
			return tuple( self.__aperture_size )
		def fset( self, value ):
			stimulus = self.stimulus
			if stimulus is None: return
			oldSize = tuple( self.__aperture_size )
			oldOffset = tuple( self.__aperture_offset )
			try: w, h = value[ :2 ]
			except: w = h = value
			x = y = 0			
			try: x, y = value[ 2: ]
			except:
				try: x, y = value[ 2 ], 0
				except: pass
			if w is not None and w < 0: w = self.__frameWidth
			if h is not None and h < 0: h = self.__frameHeight
			if w is None: w = stimulus.width
			if h is None: h = stimulus.height
			if self.__frameWidth  is not None and w > self.__frameWidth:  w = self.__frameWidth
			if self.__frameHeight is not None and h > self.__frameHeight: h = self.__frameHeight
			self.__aperture_offset = x, y
			self.__aperture_size = w, h
			if oldSize != ( w, h ) or oldOffset != ( x, y ): self.__changed = True
			stimulus.envelopeSize = self.__aperture_size
		return property( fget=fget, fset=fset )
	
	@apply
	def pan():
		def fget( self ):
			stimulus = self.stimulus
			if stimulus is None: return
			return tuple( self.__aperture_offset )
		def fset( self, value ):
			stimulus = self.stimulus
			if stimulus is None: return
			oldOffset = tuple( self.__aperture_offset )
			try: x, y = value
			except: x, y = value, 0
			self.__aperture_offset = x, y
			if oldOffset != ( x, y ): self.__changed = True
		return property( fget=fget, fset=fset )
	
	@apply
	def frame():
		def fget( self ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return None
			return self.__frameIndex
		def fset( self, value ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return
			if value in [ 'end', 'END' ]: value = self.__frameCount - 1
			if value < 0: value %= self.__frameCount
			self.__jumpToFrame = value
		return property( fget=fget, fset=fset )
	@apply
	def position():
		def fget( self ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return None
			if self.__frameIndex is None: return None
			return self.__frameIndex / self.__fps
		def fset( self, value ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return
			if value in [ 'end', 'END' ]: value = self.duration - 1.0 / self.__fps
			if value < 0: value %= self.duration
			self.__jumpToTime = value
		return property( fget=fget, fset=fset )
		
	@apply
	def source():
		def fget( self ): return self.__source
		def fset( self, value ):
			if self.__source == value: return 
			self.Close()
			self.__source = value
			self.__changed = True
			if value is None:
				self.__live = False
				self.__handle = None
			else:
				self.__live = not isinstance( value, basestring )
				self.__playing = self.__live
				try: self.__handle = cv2.VideoCapture( value, apiPreference=cv2.CAP_DSHOW if sys.platform.lower().startswith( 'win' ) else cv2.CAP_ANY )
				except: self.__handle = None
				if not self.__handle or not self.__handle.isOpened():
					self.__handle = cv2.VideoCapture( value )
				if isinstance( value, basestring ) and not os.path.isfile( value ): raise FileNotFoundError( 'could not open file %r' % value )
				# TODO: cv2 issues a warning if the file fails to load - suppress this, since the next line's exception should cover it
				if not self.__handle.isOpened(): raise IOError( 'failed to open video source %r' % value )
				self.__frameCount  = int(   self.__handle.get( getattr( cv2, 'CAP_PROP_FRAME_COUNT',  7 ) ) )
				self.__frameWidth  = int(   self.__handle.get( getattr( cv2, 'CAP_PROP_FRAME_WIDTH',  3 ) ) )
				self.__frameHeight = int(   self.__handle.get( getattr( cv2, 'CAP_PROP_FRAME_HEIGHT', 4 ) ) )
				self.__fps         = float( self.__handle.get( getattr( cv2, 'CAP_PROP_FPS',          5 ) ) )
				if not self.__fps: self.__fps = None
				self._blank = [ [ [ 0.0 ] * 4 ] * self.__frameWidth ] * self.__frameHeight
				#if self.stimulus: self.stimulus.textureSize = self.size
			self.ScheduleUpdate()
			self.position = 0 # shows initial frame, even if paused
		return property( fget=fget, fset=fset )
			
	def _AcquireFrames( self, threaded=True ):
		if threaded:
			if self.__frameQueue is not None: return
			self.__acquisitionThread = threading.Thread( target=self._AcquireFrames, kwargs=dict( threaded=False ) )
			self.__acquisitionThread.start()
			return self
		q = self.__frameQueue = []
		while self.__frameQueue is not None:
			if len( q ) > 5 or not self.__playing: break
			handle = self.__handle
			if not handle or not handle.isOpened(): break
			success, newFrame = handle.read()
			if newFrame is not None:
				newFrame = newFrame[ :, :, ::-1 ]
				self.lastFrameAcquired = newFrame
				if self.world: q.append( newFrame )
		self.__frameQueue = None # in case we got here due to a `break`
		return self
		
	def Record( self, filename, fps=15, threaded=True ):
		"""
		Record the video to file (by default, use a background thread to do
		it).
		
		Note that frame-writing has quite a CPU overhead. If `fps` is too
		high, you'll never catch up to it and the video will look too fast
		(because you're capturing frames too infrequently).
		
		Remember that the file will stay open (and potentially unflushed)
		until you `.StopRecording()`
		"""
		if threaded:
			self.__recordingThread = threading.Thread( target=self.Record, kwargs=dict( filename=filename, fps=fps, threaded=False ) )
			self.__recordingThread.start()
			return self
		try: self.__recorder.Close()
		except: pass
		recorder = self.__recorder = Utilities.VideoRecording( filename, fps=fps )
		if self.__frameQueue is None: self._AcquireFrames()
		t0 = Timing.Seconds()
		nFrames = 0
		deadline = 0
		while self.__recorder:
			deadline = t0 + nFrames / float( recorder.fps )
			while self.__recorder:
				if Timing.Seconds() >= deadline: break
				time.sleep( 0.001 )
			frame = self.lastFrameAcquired
			if frame is not None:
				if self.__recorder: recorder.WriteFrame( frame )
				if not t0: t0 = Timing.Seconds()
				nFrames += 1; 
		recorder.Close()
		return self
		
	def StopRecording( self ):
		self.__recorder = None
		
VideoSource._AttachAsProperty( Rendering.Stimulus, 'video', 'source',
	onWorldClose = lambda guest: guest.Close(),
	# onRemove = lambda host, guest: host.LoadTexture( guest._blank, False ),
	# if we comment out onRemove, then `s.source = None` would freeze the texture in place, but would still remove the `VideoSource` instance and its regularly scheduled update call
)
