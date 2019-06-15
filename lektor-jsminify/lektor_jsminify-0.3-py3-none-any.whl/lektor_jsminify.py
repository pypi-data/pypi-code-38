# -*- coding: utf-8 -*-
import os
import errno

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

    def make_sure_path_exists(path):
        # os.makedirs(path,exist_ok=True) in python3
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

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
        
        root = os.path.join(self.env.root_path, 'asset_sources/js/')make_sure_path_exists
        output = os.path.join(self.env.root_path, 'assets/js/')

        # output path has to exist
        make_sure_path_exists(output)

        for jsfile in self.find_js_files(root):
            self.minify_file(jsfile, output)

