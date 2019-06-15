# -*- coding: utf-8 -*-
import os

import rjsmin
from lektor.pluginsystem import Plugin

MINIFY_FLAG = "jsminify"

class JsminifyPlugin(Plugin):
    name = u'Lektor JSminify'
    description = u'JS minifier for Lektor. Based on rjsmin.'

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)

    def is_enabled(self, build_flags):
        return bool(build_flags.get(MINIFY_FLAG))


    def minify_file(self, target, output):
        """
        Minifies the target js file.
        """
        result = None
        with open(target, 'r') as fr:
            result = rjsmin.jsmin(fr.read())

        if result == None:
            return
    
        filename = os.path.basename(target)
        output_file = os.path.join(output, filename)
        if not output_file.endswith('.min.js'):
            output_file = output_file.replace('.js', '.min.js')
        with open(output_file, 'w') as fw:
            fw.write(result)

    def find_js_files(self, destination):
        """
        Finds all js files in the given destination.
        """
        for root, dirs, files in os.walk(destination):
            for f in files:
                if f.endswith('.js'):
                    yield os.path.join(root, f)


    def on_before_build_all(self, builder, **extra):
        try: # lektor 3+
            is_enabled = self.is_enabled(builder.extra_flags)
        except AttributeError: # lektor 2+
            is_enabled = self.is_enabled(builder.build_flags)

        if not is_enabled:
            return
        
        root = os.path.join(self.env.root_path, 'asset_sources/js/')
        output = os.path.join(self.env.root_path, 'assets/js/')

        for jsfile in self.find_js_files(root):
            self.minify_file(jsfile, output)

