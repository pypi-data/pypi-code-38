"""
Makes the list, dict, and set built-in types into Pluckables.
Warning, this depends on the forbiddenfruit library, which
is self proclaimed to be super hacky and not production ready.
Use at your own discretion.

usage:  just import this package and you're good to go,
eg. `import pluckit.native`
"""

from .pluck import pluck

try:
    import forbiddenfruit
except ImportError:
    raise ImportError(
      'manual install needed: `pip install forbiddenfruit`'
    )

__all__ = [ 'install', 'uninstall' ]


cursed_types = set()

def install(types):
    for _type in types:
        forbiddenfruit.curse(_type, 'pluck', pluck)
        cursed_types.add(_type)


def uninstall(types = None):
    if types is None:
        # uninstall everything
        types = list(cursed_types)

    for _type in types:
        forbiddenfruit.reverse(_type, 'pluck')
        cursed_types.remove(_type)



# wire it up
install([ dict, list, set, tuple ])
