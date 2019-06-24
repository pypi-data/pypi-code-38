from .base import BaseProcessor

class PlainProcessor(BaseProcessor):

    def process(self, input, vars):
        return input