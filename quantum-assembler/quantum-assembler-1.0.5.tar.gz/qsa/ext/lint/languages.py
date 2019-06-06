import itertools
import os
import re


class BaseLanguageDetector:
    name = None


class ExtensionBasedLanguageDetector(BaseLanguageDetector):
    # A regex pattern to determine the programming or markup
    # language based on the file extension.
    pattern = None

    # Patterns to ignore
    ignored_dirs = ['.git', 'build', 'env', 'lib', 'dist']

    def __init__(self):
        assert self.pattern is not None
        self.re = re.compile(self.pattern)

    def detect(self):
        """Return a boolean indicating if the project contains sources for
        the configured programming or markup language.
        """
        result = False
        for root, dirnames, filenames in os.walk('.'):
            basedir = root[2:]
            if basedir.split('/', 1)[0] in self.ignored_dirs:
                continue
            for fn in filenames:
                if self.re.match(fn):
                    path = os.path.join(root, fn)
                    result = True
                    break

        return result


class YAMLDetector(ExtensionBasedLanguageDetector):
    pattern = '^.*\.(yaml|yml)$'
