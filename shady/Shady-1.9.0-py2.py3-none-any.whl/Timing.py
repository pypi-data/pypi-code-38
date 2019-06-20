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
	'Seconds',
	'MillisecondsSince',
	
	'SetProcessPriority',
	'SetThreadPriority',
	'SetProcessAffinity',
	'SetThreadAffinity',
]

import sys
import time
import ctypes

WINDOWS = sys.platform.lower().startswith( 'win' )

# Precision time measurement
# First set some (non-Windows) fallbacks before replacing them with Windows API calls below
# TODO: verify/improve precision on non-Windows platforms?
try:    Seconds = time.monotonic   # only available in Python 3.3+
except: Seconds = time.time        # vulnerable to system clock updates over network

def MillisecondsSince( t0_seconds ):
	return ( Seconds() - t0_seconds ) * 1000.0

def Message( msg ):
	print( msg )

class ProcessAPIError( Exception ): pass
class ThreadAPIError(  Exception ): pass
def SetThreadAffinity( affinity ):  Message( "cannot adjust thread affinity"  )
def SetThreadPriority( priority ):  Message( "cannot adjust thread priority"  )
def SetProcessAffinity( affinity ): Message( "cannot adjust process affinity" )
def SetProcessPriority( priority ): Message( "cannot adjust process priority" )


if WINDOWS:
	
	DWORD = ctypes.c_uint32
	HANDLE = ctypes.c_voidp
	LARGE_INTEGER = ctypes.c_int64
	
	kernel32dll = ctypes.windll.kernel32
	
	( kernel32dll.QueryPerformanceCounter, kernel32dll.QueryPerformanceFrequency )
	def Seconds():
		counter  = LARGE_INTEGER()
		timebase = LARGE_INTEGER()
		kernel32dll.QueryPerformanceCounter( ctypes.byref( counter ) )
		kernel32dll.QueryPerformanceFrequency( ctypes.byref( timebase ) )
		return 	counter.value / float( timebase.value )
	
	PROCESS_PRIORITIES = {
		'REALTIME_PRIORITY_CLASS':         0x00000100,
		'HIGH_PRIORITY_CLASS':             0x00000080,
		'ABOVE_NORMAL_PRIORITY_CLASS':     0x00008000,
		'NORMAL_PRIORITY_CLASS':           0x00000020,
		'BELOW_NORMAL_PRIORITY_CLASS':     0x00004000,
		'IDLE_PRIORITY_CLASS':             0x00000040,
		
		                            +3:    0x00000100,
		                            +2:    0x00000080,
		                            +1:    0x00008000,
		                             0:    0x00000020,
		                            -1:    0x00004000,
		                            -2:    0x00000040,
	}
	THREAD_PRIORITIES = {
		'THREAD_PRIORITY_TIME_CRITICAL':   15,
		'THREAD_PRIORITY_HIGHEST':          2,
		'THREAD_PRIORITY_ABOVE_NORMAL':     1,
		'THREAD_PRIORITY_NORMAL':           0,
		'THREAD_PRIORITY_BELOW_NORMAL':    -1,
		'THREAD_PRIORITY_LOWEST':          -2,
		'THREAD_PRIORITY_IDLE':           -15,
	
		                            +3:    15,
		                            +2:     2,
		                            +1:     1,
		                             0:     0,
		                            -1:    -1,
		                            -2:    -2,
		                            -3:   -15,
	}


	( kernel32dll.GetCurrentProcess, kernel32dll.SetProcessAffinityMask, kernel32dll.SetPriorityClass )
	def SetProcessPriority( priority ):
		priority = PROCESS_PRIORITIES.get( priority, priority )
		if priority not in PROCESS_PRIORITIES.values(): raise ProcessAPIError( 'unrecognized priority value %r' % priority )
		result = kernel32dll.SetPriorityClass( HANDLE( kernel32dll.GetCurrentProcess() ), DWORD( priority ) )
		if result == 0: raise ProcessAPIError( 'SetPriorityClass call failed' )
	def SetProcessAffinity( affinity ):
		if isinstance( affinity, ( tuple, list ) ): affinity = sum( ( 2 ** i ) if x else 0 for i, x in enumerate( affinity ) )
		result = kernel32dll.SetProcessAffinityMask( HANDLE( kernel32dll.GetCurrentProcess() ), DWORD( affinity ) )
		if result == 0: raise ProcessAPIError( 'SetProcessAffinityMask call failed' )

	( kernel32dll.GetCurrentThread, kernel32dll.SetThreadAffinityMask, kernel32dll.SetThreadPriority )
	def SetThreadPriority( priority ):
		priority = THREAD_PRIORITIES.get( priority, priority )
		if priority not in THREAD_PRIORITIES.values(): raise ThreadAPIError( 'unrecognized priority value %r' % priority )
		result = kernel32dll.SetThreadPriority( HANDLE( kernel32dll.GetCurrentThread() ), ctypes.c_int( priority ) )
		if result == 0: raise ThreadAPIError( 'SetThreadPriority call failed' )
	def SetThreadAffinity( affinity ):
		if isinstance( affinity, ( tuple, list ) ): affinity = sum( ( 2 ** i ) if x else 0 for i, x in enumerate( affinity ) )
		result = kernel32dll.SetThreadAffinityMask( HANDLE( kernel32dll.GetCurrentThread() ), DWORD( affinity ) )
		if result == 0: raise ThreadAPIError( 'SetThreadAffinityMask call failed' )	

def TimerResolutionInMilliseconds( func=Seconds ): # make sure this is defined *after* any platform-specific redefinition of Seconds
	func()
	a = b = func() * 1000.0
	while b - a == 0.0:  b = func() * 1000.0
	a = b
	while b - a == 0.0:  b = func() * 1000.0
	return b - a

RESOLUTION_MSEC = TimerResolutionInMilliseconds()
if RESOLUTION_MSEC > 0.08: Message( __name__ + ' module could not find a precision timer: resultion is %g ms' % RESOLUTION_MSEC )
