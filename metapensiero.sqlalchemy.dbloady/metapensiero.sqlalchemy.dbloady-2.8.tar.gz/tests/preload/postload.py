# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Sample postload script
# :Created:   gio 14 gen 2016 11:36:58 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import datetime
import model

event = session.query(model.Event).first()

assert event.starttime == datetime.time(12, 23)
assert event.endtime == datetime.time(15, 34)
