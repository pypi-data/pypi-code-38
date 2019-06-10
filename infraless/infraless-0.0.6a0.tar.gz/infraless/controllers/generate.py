#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stocksense/controllers/stock.py

"""
import os

from cement import Controller, ex
from PyInquirer import Token, prompt, style_from_dict

from ..controllers.validators import EmptyValidator
from ..core import config
from ..core import helpers as hlprs
from ..core.exc import InfralessError

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})


class Generate(Controller):
    class Meta:
        label = 'g'
        description = "Generate modules"
        stacked_on = 'base'
        stacked_type = 'nested'

    @ex(
        help='Generate modules and automated code', )
    def engine(self):
        config.validate_ilconfig()
        hlprs.log("Engine added", "green")
