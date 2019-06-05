import glob
import setuptools

import cmstoolbox

setuptools.setup(
    name='cmstoolbox',
    version=cmstoolbox.__version__,
    packages=setuptools.find_packages(),
    author='Daniel Abercrombie',
    author_email='dabercro@mit.edu',
    description='Tools used by CMS Computing Operations',
    url='https://github.com/CMSCompOps/OpsSpace',
    scripts=[s for s in glob.glob('bin/*') if not s.endswith('~')]
    )
