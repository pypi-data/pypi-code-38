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
Shady is a software engine/toolbox that enables precise presentation of visual stimuli on 
mass-produced screens and video cards, without additional specialized hardware. It is 
aimed at programmers who work in neuroscience---especially vision science. It allows you 
to render arbitrary stimulus patterns linearly with high dynamic range and high timing 
precision. It lets you manipulate them in real time while leaving the CPU maximally free 
to perform other time-critical tasks. To do this, it provides a customizable, specialized 
"shader" program that runs on the GPU, and a high-level wrapper/API in Python. 

The Python-language parts of Shady are organized into various submodules, but all the 
symbols exported by the submodules (and hence, pretty much all the features of Shady 
you'll ever want to use) are also available in the top-level namespace. So, for example,
`Shady.Rendering.World` is also available as simply `Shady.World`;  
`Shady.Dynamics.Integral` is also available as `Shady.Integral`; 
`Shady.Utilities.FrameIntervalGauge` is also available as `Shady.FrameIntervalGauge`.

Under the hood, Shady's frame-by-frame CPU operations are performed by an engine which 
can, in principle, use pure Python code (there is a pure-Python implementation, included
as a fallback, in `Shady.PyEngine`). However, for various performance-related reasons, it
is highly recommended better to use the "accelerator", which is an engine compiled from 
C++ and packaged as a dynamic library called ShaDyLib.  Some binary builds of ShaDyLib are
included with the Shady Python package: `.dll` files for 32- and 64-bit Windows, and a 
`.dylib` file for 64-bit macOS 10.9 and up. These are used by default where possible.    
For earlier macOS versions (back as far as 10.4) or to make the corresponding `.so` file 
for Linux, you would need to build from the C++ sources - see 
`Shady.Documentation.Accelerator` for more details.

The best place to learn about Shady is the project homepage (see `Shady.__homepage__`)
but much of the documentation available there is also available at the Python or IPython 
prompt, in the docstrings of objects defined in the `Shady.Documentation` submodule.

Various example scripts are provided to help in learning Shady concepts and techniques. 
These can be explored as follows::

	python -m Shady EXAMPLE_NAME         # Run the named example (press q to quit).
	python -m Shady EXAMPLE_NAME --help  # Most of the examples support additional 
	                                     # command-line options, including --help which
	                                     # provides documentation for those options.

The above syntax implicitly uses the `run` subcommand.  Other subcommands are available::
	                                     
	python -m Shady list                 # List the available examples.
	python -m Shady help                 # Print the full documentation for `-m Shady`.
	python -m Shady help EXAMPLE_NAME    # Same as `python -m Shady EXAMPLE_NAME --help`.
	python -m Shady demo EXAMPLE_NAME    # Run the named example interactively.

That last form can be very handy.  Shady is designed to allow programmers to build and 
test their stimulus arrangements interactively in real time. The "demo" subcommand allows
each example script to be run step-by-step, with an interactive prompt that allows you to
experiment with stimulus parameters as you wish.  You can also enter an "empty" 
interactive demo by saying simply  `python -m Shady` and creating your own `World` from
the prompt.

The best starting point is probably as follows::

	python -m Shady demo showcase

"""
#from . import DependencyManagement; DependencyManagement.Sabotage( 'numpy', 'Image', 'ImageDraw', 'ImageFont', 'matplotlib', 'cv2', 'OpenGL', 'serial' ) # !!!! for debugging only

from . import DPI;           from .DPI           import *
from . import Timing;        from .Timing        import *
from . import Location;      from .Location      import *
from . import Dynamics;      from .Dynamics      import *
from . import Contrast;      from .Contrast      import *
from . import Utilities;     from .Utilities     import *
from . import Rendering;     from .Rendering     import *
from . import Linearization; from .Linearization import *

from . import Documentation
from . import Testing

from .Rendering import __version__, __meta__
__homepage__ = __meta__[ 'homepage' ]
