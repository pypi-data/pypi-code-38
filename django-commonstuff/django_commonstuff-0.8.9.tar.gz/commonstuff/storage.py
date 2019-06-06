# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import csscompressor
import jsmin

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.contrib.staticfiles.utils import matches_patterns
from django.core.files.base import ContentFile
from django.conf import settings

from .settings import MINIFY_CSS, MINIFY_JS


class MinifyStaticFilesStorage(StaticFilesStorage):

    def __get_patterns(self, anti=False):
        patterns = []
        
        if MINIFY_CSS:
            patterns.append("*.css")
        if MINIFY_JS:
            patterns.append("*.js")
        
        if anti:
            patterns = [ x.replace('*.', '*.min.') for x in patterns ]
        
        return tuple(patterns)
    
    def post_process(self, paths, dry_run=False, **options):
        # call parent postprocessors
        parent = super(MinifyStaticFilesStorage, self)
        if hasattr(parent, 'post_process'):
            for original_path, processed_path, processed \
                in parent.post_process(paths.copy(), dry_run, **options):
                if processed_path != original_path:
                    if original_path in paths:
                        del paths[original_path]
                    paths[processed_path] = (self, processed_path)
                yield original_path, processed_path, processed
        
        if dry_run:
            return
        
        # minify
        print("Minify %s files." % ', '.join(self.__get_patterns()))
        for path in paths:
            if not path:
                continue
            if not matches_patterns(path, self.__get_patterns()):
                continue
            if matches_patterns(path, self.__get_patterns(anti=True)):
                continue
            
            original_file_content = self.open(path).read()
            original_file_content = original_file_content.decode(settings.DEFAULT_CHARSET)
            minified_file_content = None
            if str(path)[-3:] == 'css':
                minified_file_content = csscompressor.compress(original_file_content)
            elif str(path)[-2:] == 'js':
                minified_file_content = jsmin.jsmin(original_file_content)
            
            if minified_file_content is not None \
                and len(minified_file_content) < len(original_file_content):
                if self.exists(path):
                    self.delete(path)
                _ = self.save(path, ContentFile(minified_file_content))
                yield path, path, True
        