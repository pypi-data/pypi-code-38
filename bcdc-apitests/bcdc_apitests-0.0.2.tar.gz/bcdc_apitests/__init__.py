'''
package metadata.

:ivar name: the name of the package. any time the package name is required for
    example from the setup.py it gets retrieved from here.
:ivar version: This is optional!  By default when a new pypi package is built 
    it will determine the existing package version from pypi and increment the 
    minor package version by 1.  If you wish to override this behaviour you can 
    hardcode the version in this file.
'''

name = 'bcdc_apitests'
version = '0.0.1'
