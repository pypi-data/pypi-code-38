# # # # # # # # # # # # # # # # # # # # # # # # # #
# Reporting
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from .formatter import compactify

def report (instance, method, extras = {}):
    ''' Report name, method, root, sandbox, and any specified extras provided verbosity is enabled.'''

    if not hasattr (instance, "verbosity"):
        return

    if instance.verbosity:
        identifiers = []
        if hasattr (instance, 'root'):
            identifiers += ['root - ' + compactify (instance.root)]
        if instance.sandboxing and hasattr (instance, 'sandbox'):
            identifiers += ['sandbox - %s' % instance.sandbox ()]
        print (" :: %s in '%s': %s" % (instance.name, method, ', '.join (identifiers)))
        for key, extra in extras.items ():
            print ('  : -> %s: %s' % (key, str (extra)))