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

#: How to customize signal, modulation or windowing functions
"""
This script demonstrates how you can easily extend the GPU shader
program with custom variables (called "uniform variables"), custom
carrier signal functions, custom contrast modulation functions,
and custom windowing functions.  You write the functions as small
pieces of GL Shading Language code.

Assuming you use the ShaDyLib binary accelerator as a back-end,
this demo does not use *any* third-party Python packages.
"""#.

if __name__ == '__main__':
	
	"""
	Let's get the command-line arguments out the way first
	"""#:
	import Shady
	cmdline = Shady.WorldConstructorCommandLine( canvas=True, reportVersions=True )
	cmdline.Help().Finalize()
	
	"""
	Customization is performed *before* any instances
	of `World` or `Stimulus` are created.  Let's start by defining
	a custom signal function.  A signal function is written in
	GLSL and follows one of the following two prototypes::
	
	    float func( vec2 coords ) { ... }   // monochromatic output
	    vec3  func( vec2 coords ) { ... }   // RGB output
	
	where `coords` is a 2-D coordinate in pixels measured from the
	center of the stimulus.
	"""#.

	"""
	The one pre-existing signal function is called `SinewaveSignal`,
	which has the associated index number 1.  Signal function names
	are mapped to numbers in the namespace `Shady.SIGFUNC`:
	"""#:

	print( Shady.SIGFUNC.SinewaveSignal )

	"""
	More names will appear in this namespace as you define more
	functions yourself. The idea is that, while you can activate the
	sine-wave signal function for your stimulus instance `stim` by
	saying::
	
	    stim.signalFunction = 1
	
	it makes for more transparent, readable code if you express
	that as::
	
	    stim.signalFunction = Shady.SIGFUNC.SinewaveSignal
	
	Let's look at the source code for `SinewaveSignal` in the actual
	shader program:
	"""#.

	sourceFileName = Shady.PackagePath( 'glsl/FragmentShader.glsl' )
	sourceCode = open( sourceFileName ).read()
	import re
	match = re.search( r'\n\S+\s+SinewaveSignal\s*\(.+?\)\s*\{.+?\n}', sourceCode, re.S)
	if match :print( match.group() )
	
	"""
	(retrieved from glsl/FragmentShader.glsl) inside the Shady package).
	"""#.

	"""
	You'll see that `SinewaveSignal` uses a variable called
	`uSignalParameters`. This is a "uniform" variable in the shader,
	meaning that its value does not change from pixel to pixel in a
	given stimulus and that we are able to change its value from the
	CPU side. According to Shady's naming conventions, the
	`uSignalParameters` variable receives its value from a managed
	property called `.signalParameters` (which, in this case, belongs
	only to the `Stimulus` class).
	
	The function also uses the `sinusoid()` helper function. For our
	first example, let's use both of these pre-existing tools to
	implement an antialiased square-wave signal function, as a
	finite sum of sinusoid() components. We'll do this with the
	global function `AddCustomSignalFunction`, to which we need to
	pass a multi-line string containing the GLSL shader code:
	"""#:
	
	Shady.AddCustomSignalFunction("""
	
	float SquarewaveSignal( vec2 coords )
	{
		float y = 0.0;
		for( float harmonic = 1.0; ; harmonic += 2.0 )
		{
			float cyclesPerPixel = uSignalParameters[ 1 ] * harmonic;
			if( cyclesPerPixel > 0.5 ) break;
			y += sinusoid(
				coords,
				cyclesPerPixel,
				uSignalParameters[ 2 ],
				harmonic * uSignalParameters[ 3 ]
			) * uSignalParameters[ 0 ] / harmonic;
		}
		return y;
	}
	
	""")

	"""
	Note that this has automatically added a new index to the
	`Shady.SIGFUNC` namespace:
	"""#:

	print( Shady.SIGFUNC.SquarewaveSignal )

	"""
	For our next trick, let's make a signal function that displays
	a frozen random uniform noise.  We can use the helper function
	`random()` which takes a 2-dimensional coordinate as its seed,
	and returns a pseudo-random number from the uniform distribution
	over the range [-1, +1]. For scaling we'll use the existing
	`.signalAmplitude` property which is a shortcut to the first
	element of the `.signalParameters` property, and hence to the
	first element of the `uSignalParameters` uniform variable in the
	shader.
	"""#:

	Shady.AddCustomSignalFunction("""
	float RandomSignal( vec2 coords )
	{
		vec3 seed3 = vec3( ( 1.0 + coords ) / ( 2.0 + uTextureSize ),  uSeed );
		return random( seed3 ) * uSignalParameters[ 0 ]; // output of random() is the range [-1, +1]
	}
	""")

	"""
	Note that we also introduced a customizable random-seed as the
	uniform variable `uSeed`. This does not exist yet, but it can
	be created, and manipulated as a `Stimulus` property, if we use
	the property name 'seed':
	"""#:

	Shady.Stimulus.AddCustomUniform( seed=1.0 )
	# Note that this is not a global function, but rather a class
	# method of the `Stimulus` class.  You can also add custom
	# properties/uniform variables to the `World` class if you want.

	"""
	Let's do another one.  What else do psychophysicists like?
	Of course: plaids!  Let's create a Plaid() signal function,
	parameterizing the angle between plaid components with another
	new uniform:
	"""#:

	Shady.Stimulus.AddCustomUniform( plaidAngle=90.0 )
	Shady.AddCustomSignalFunction("""
	float Plaid( vec2 coords )
	{
		return uSignalParameters[ 0 ] * (
			  sinusoid( coords, uSignalParameters[ 1 ], uSignalParameters[ 2 ] - uPlaidAngle / 2.0, uSignalParameters[ 3 ] )
			+ sinusoid( coords, uSignalParameters[ 1 ], uSignalParameters[ 2 ] + uPlaidAngle / 2.0, uSignalParameters[ 3 ] )
		);
	}
	""")

	"""
	Hopefully you've got the idea how to customize signal
	functions.  What about contrast-modulation functions?
	You may have noticed that we carefully included the
	word "Signal" in the name `SquarewaveSignal`.  This
	allows us to mirror the existing distinction, in the
	shader, between `SinewaveSignal` and
	`SinewaveModulation`, which is important because the
	two functions use different uniform variables for their
	parameters, and a different convention for interpreting
	the amplitude parameter.
	
	Modulation functions always have scalar output, so their
	prototype is always::
	
	    float f( vec2 coords ) { ... }  # scalar output only
	
	With all of this in mind, let's make the analogous
	`SquarewaveModulation` function:
	"""#:

	Shady.AddCustomModulationFunction("""
	float SquarewaveModulation( vec2 coords )
	{
		// NB: *not* spatially antialiased (that's left as an exercise for the reader)
		float y = sign( sinusoid( coords, uModulationParameters[ 1 ], uModulationParameters[ 2 ], uModulationParameters[ 3 ] ) );
		return 1.0 + uModulationParameters[ 0 ] * ( y - 1.0 ) / 2.0;
	}
	""") # result will be registered in the Shady.MODFUNC namespace

	"""
	Finally, the last class of functions that is customizable
	is the windowing function. The prototype for a custom
	windowing function is::
	
	    float f( float r ) { ... }
	
	where r varies between 0 at the peak (or throughout the
	plateau, if any) and 1 at the edge of the stimulus. So,
	if you absolutely positively have to have, say,
	Blackman-Harris windows instead of Hann windows:
	"""#:

	Shady.AddCustomWindowingFunction("""
	float BlackmanHarris( float r )
	{
		r += 1.0;
		r *= PI;
		float w = 0.35875;
		w += -0.48829 * cos( r );
		w += +0.14128 * cos( r * 2.0 );
		w += -0.01168 * cos( r * 3.0 );
		return w;
	}
	""") # result will be registered in the Shady.WINFUNC namespace

	"""
	...or Gaussian windows, extending out to a configurable
	number of sigmas:
	"""#:
	Shady.Stimulus.AddCustomUniform( gaussianSigmas=3.0 )
	Shady.AddCustomWindowingFunction("""
	float Gaussian( float r )
	{
		r *= uGaussianSigmas;
		float v = exp( -0.5 * r * r );
		// uncomment the following to ensure the window really comes down to zero:
		// float tailThickness = exp( -0.5 * uGaussianSigmas * uGaussianSigmas );
		// v = ( v - tailThickness ) / ( 1.0 - tailThickness );
		return v;
	}
	""") # result will be registered in the Shady.WINFUNC namespace

	"""
	# All of this customization had to be done *before* `World`
	# initialization. Now let's put it all together, and test each
	# of our custom additions.  First, create a `World`:
	"""#:

	w = Shady.World( **cmdline.opts ).Set( gamma=2.2 )

	"""
	Now the stimuli.  First, a square-wave signal patch,
	windowed a la Blackman-Harris:
	"""#:

	s1 = w.Stimulus(
		size = 500,
		x = -250,
		y = +250,
		plateauProportion = 0, # non-negative: turns windowing on
		windowingFunction = Shady.WINFUNC.BlackmanHarris,  # custom
		signalAmplitude = 0.5,
		signalFunction = Shady.SIGFUNC.SquarewaveSignal,   # custom
		atmosphere = w,
	)

	"""
	Then a plaid, with the usual Hann window:
	"""#:

	s2 = w.Stimulus(
		size = 500,
		x = +250,
		y = +250,
		plateauProportion = 0, # non-negative: turns windowing on
		signalFunction = Shady.SIGFUNC.Plaid,  # custom
		signalAmplitude = 0.25,
		signalOrientation = 45,
		atmosphere = w,
	)

	"""
	Now a frozen noise, again in a Hann window:
	"""#:

	s3 = w.Stimulus(
		size = 500,
		x = -250,
		y = -250,
		plateauProportion = 0, # non-negative: turns windowing on
		signalFunction = Shady.SIGFUNC.RandomSignal,
		signalAmplitude = 0.5,
		atmosphere = w,
	)

	"""
	And finally a Gabor with additional square-wave
	contrast modulation:
	"""#:

	s4 = w.Stimulus(
		size = 500,
		x = +250,
		y = -250,
		plateauProportion = 0, # non-negative: turns windowing on
		signalFunction = Shady.SIGFUNC.SinewaveSignal,
		signalAmplitude = 0.5,
		modulationFunction = Shady.MODFUNC.SquarewaveModulation,
		modulationDepth = 1.0,
		modulationFrequency = 0.01,
		modulationOrientation = 45,
		atmosphere = w,
	)

	"""
	Now let's animate some aspects of our stimuli, including
	the new property `.plaidAngle` in the plaid stimulus:
	"""#:

	s1.cx = Shady.Integral( 50 )
	s1.windowingFunction = lambda t: \
		Shady.WINFUNC.BlackmanHarris if 0 <= ( t % 3 ) < 1    else \
		Shady.WINFUNC.Gaussian       if 1 <= ( t % 3 ) < 2    else \
		Shady.WINFUNC.Hann
	s2.plaidAngle = Shady.Oscillator( 0.2 ) * 45 + 45
	s3.seed = lambda t: 1 + int( t )
	s4.modulationDepth = Shady.Oscillator( 0.2 ) * 0.5 + 0.5

	""#.
	Shady.AutoFinish( w ) # tidying up in case we didn't get here via `python -m Shady`
