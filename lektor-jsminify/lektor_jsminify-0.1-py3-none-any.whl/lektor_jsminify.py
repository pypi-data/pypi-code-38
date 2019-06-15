# -*- coding: utf-8 -*-
import os
import codecs
import chardet
import sys

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


    def minify_file(self, target):
        """
        Minifies the target js file.
        """
        with open(target, 'r+') as f:
            result = rjsmin.jsmin(f.read())
            f.seek(0)
            f.write(result)
            f.truncate()

    def find_js_files(self, destination):
        """
        Finds all js files in the given destination.
        """
        for root, dirs, files in os.walk(destination):
            for f in files:
                if f.endswith('.js'):
                    yield os.path.join(root, f)


    def on_after_build_all(self, builder, **extra):

        try: # lektor 3+
            is_enabled = self.is_enabled(builder.extra_flags)
        except AttributeError: # lektor 2+
            is_enabled = self.is_enabled(builder.build_flags)

        if not is_enabled:
            return

        for jsfile in self.find_js_files(builder.destination_path):
            self.minify_file(jsfile)

