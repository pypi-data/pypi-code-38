from setuptools import setup
 
setup(
     name='qwackchat',    # This is the name of your PyPI-package.
     version='0.1.7.5',                          # Update the version number for new releases
     scripts=['qwackchat=qwackchat.pyw','sqwackchat=sqwackchat.pyw','gui.py']                  # The name of your scipt, and also the command you'll be using for calling it
)
