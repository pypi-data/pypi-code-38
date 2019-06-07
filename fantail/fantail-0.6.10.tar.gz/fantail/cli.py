# -*- coding: utf-8 -*-

import os
import fantail

def dispatch():
    """
    Run the app - this is the actual entry point
    """
    app.run()

app = leip.app(name='fantail', set_name=None)
app.discover(globals())
