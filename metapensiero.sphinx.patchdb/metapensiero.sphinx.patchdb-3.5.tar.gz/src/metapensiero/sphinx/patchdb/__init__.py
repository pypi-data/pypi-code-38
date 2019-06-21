# -*- coding: utf-8 -*-
# :Project:   PatchDB -- PatchingRST
# :Created:   Fri Oct  3 00:37:54 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2009, 2012, 2013, 2016, 2017 Lele Gaifax
#

def setup(app):
    "Setup the Sphinx environment."

    if not hasattr(app, 'add_config_value'):
        # Silly nosetests!
        return

    from .locale import setup as setup_i18n
    from .script import setup as setup_script

    # This is the pickle where we store the found scripts, at the
    # end of the build
    app.add_config_value('patchdb_storage', None, False)

    setup_i18n(app)
    setup_script(app)
