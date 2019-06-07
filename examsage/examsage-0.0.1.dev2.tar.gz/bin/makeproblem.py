#!/usr/bin/env python3

from examsage import Problem
from pathlib import Path
from shutil import copy

### DEBUG: The CoCalc LaTeX editor keeps issuing an error associated with Pickle. It appears that the editor is using the Python 2.7 version of Pickle instead of the required 3.2+ version.
import sys
print("sys.version_info.major is " + str(sys.version_info.major))
print(sys.version_info)

##RESULT:
#    sys.version_info.major is 3
#    sys.version_info(major=3, minor=6, micro=7, releaselevel='final', serial=0)
### DEBUG: The CoCalc LaTeX editor keeps issuing an error associated with Pickle. It appears that the editor is using the Python 2.7 version of Pickle instead of the required 3.2+ version.

# Create the problem
path = Path.cwd()
prbm = Problem(path)

# Create the latexmk output directory if necessary
out_dir = path / 'build'
out_dir.mkdir(parents=True, exist_ok=True)

# Run latexmk
filename = out_dir / prbm.name
#print(prbm.dumps())
prbm.generate_pdf(filename, clean=False, clean_tex=False, instructor_key=True) # , compiler_args=['-f', '-g' , '-bibtex', '-synctex=1']

# Copy the PDF to body.pdf for the CoCalc LaTeX editor
source = str(filename.with_suffix('.pdf'))
dest = str(path / ('body' + '.pdf'))
copy(source, dest)