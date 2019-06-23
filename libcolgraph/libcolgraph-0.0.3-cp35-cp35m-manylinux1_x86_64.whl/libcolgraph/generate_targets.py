#!/usr/bin/env python3

from distutils.core import Extension

if __name__ == '__main__':
    import setup
    stuff = dir(setup)

    modules = [setup.__dict__[item] for item in stuff
               if type(setup.__dict__[item]) is Extension]
    sources = sum([module.sources for module in modules], [])

    print(' '.join(sources), end='')
