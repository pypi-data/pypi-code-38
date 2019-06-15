# -*- coding: utf-8 -*-
import os

import sass
from lektor.pluginsystem import Plugin

COMPILE_FLAG = "scsscompile"

class ScsscompilePlugin(Plugin):
    name = u'Lektor SCSScompile'
    description = u'SASS compiler for Lektor, thats based on libsass.'

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

    def is_enabled(self, build_flags):
        return bool(build_flags.get(COMPILE_FLAG))

    def on_before_build_all(self, builder, **extra):
        try: # lektor 3+
            is_enabled = self.is_enabled(builder.extra_flags)
        except AttributeError: # lektor 2+
            is_enabled = self.is_enabled(builder.build_flags)

        if not is_enabled:
            return
        
        root_scss = os.path.join(self.env.root_path, 'asset_sources/scss/')
        output = os.path.join(self.env.root_path, 'assets/css/')

        sass.compile(dirname=(root_scss, output), output_style='compressed')

