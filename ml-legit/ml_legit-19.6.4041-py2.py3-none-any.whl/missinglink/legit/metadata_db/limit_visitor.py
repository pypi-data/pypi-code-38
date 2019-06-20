# -*- coding: utf-8 -*-
from ..scam import MLQueryVisitor


# noinspection PyClassicStyleClass
class LimitVisitor(MLQueryVisitor):
    def __init__(self):
        self.limit = None

    def visit_function_limit(self, node, parents=None, context=None):
        self.limit = node.limit
