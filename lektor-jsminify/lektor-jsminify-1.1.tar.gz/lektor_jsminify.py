# -*- coding: utf-8 -*-
import os
import errno
import re

import rjsmin
from lektor.pluginsystem import Plugin
from termcolor import colored

MINIFY_FLAG = "jsminify"

class JsminifyPlugin(Plugin):
    name = u'Lektor JSminify'
    description = u'JS minifier for Lektor. Based on rjsmin.'

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        config = self.get_config()
        self.source_dir = config.get('source_dir', 'asset_sources/js/')
        self.output_dir = config.get('output_dir', 'assets/js/')
        self.name_prefix = config.get('name_prefix', '')
        self.keep_bang_comments = config.get('keep_bang_comments', 'False')

    def is_enabled(self, build_flags):
        return bool(build_flags.get(MINIFY_FLAG))

# .*\.min\.js
    def minify_file(self, target, output):
        """
        Minifies the target js file.
        """
        #if (re.match(self.exclude, target) and not re.match(self.include, target)):
        #    return

        filename = os.path.basename(target)
        output_file = os.path.join(output, filename)
        file_end = self.name_prefix + '.js'
        if not output_file.endswith(file_end):
            output_file = output_file.replace('.js', file_end)

        # check if file has been changed after output file ()
        if (os.path.isfile(output_file) and os.path.getmtime(target) <= os.path.getmtime(output_file)):
            return

        result = None
        with open(target, 'r') as fr:
            result = rjsmin.jsmin(fr.read(), self.keep_bang_comments.lower()=='true')

        if result == None:
            return
    
        
        with open(output_file, 'w') as fw:
            fw.write(result)
        print(colored('js', 'green') + ' ' + self.source_dir + os.path.basename(target) + ' -> ' + self.output_dir + os.path.basename(output_file))

    def make_sure_path_exists(self, path):
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
        
        root_js = os.path.join(self.env.root_path, self.source_dir )
        output = os.path.join(self.env.root_path, self.output_dir )

        # output path has to exist
        self.make_sure_path_exists(output)

        for jsfile in self.find_js_files(root_js):
            self.minify_file(jsfile, output)