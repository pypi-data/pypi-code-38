# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Product-related commands
"""

from __future__ import unicode_literals, absolute_import

import logging

from rattail.commands.core import Subcommand, date_argument
from rattail.time import make_utc


log = logging.getLogger(__name__)


class UpdateCosts(Subcommand):
    """
    Update (move future to current) costs for all products
    """
    name = 'update-costs'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.")

    def run(self, args):
        from rattail.db.api.products import make_future_cost_current
        from rattail.db.continuum import versioning_manager

        session = self.make_session()
        model = self.model
        user = self.get_runas_user(session)
        session.set_continuum_user(user)

        # TODO: even if this works, it seems heavy-handed...
        # (also it *doesn't* work if ran before setting continuum user)
        uow = versioning_manager.unit_of_work(session)
        transaction = uow.create_transaction(session)
        transaction.meta = {'comment': "make future costs become current"}

        now = make_utc()
        future_costs = session.query(model.ProductFutureCost)\
                              .filter(model.ProductFutureCost.starts <= now)\
                              .all()
        log.info("found %s future costs which should become current", len(future_costs))

        def move(future, i):
            make_future_cost_current(self.config, future)

        self.progress_loop(move, future_costs,
                           message="Making future costs become current")

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        else:
            session.commit()
            log.info("transaction was committed")
        session.close()
