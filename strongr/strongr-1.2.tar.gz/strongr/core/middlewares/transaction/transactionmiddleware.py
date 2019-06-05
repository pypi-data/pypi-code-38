from cmndr import Middleware
from sqlalchemy.exc import SQLAlchemyError

import logging


class TransactionMiddleware(Middleware):
    def execute(self, command, next_callable):
        import strongr.core
        if hasattr(strongr.core.Core.config(), 'db') and hasattr(strongr.core.Core.config().db, 'engine'):
            import strongr.core.gateways

            session = strongr.core.gateways.Gateways.sqlalchemy_session()

            try:
                ret = next_callable(command)
                session.commit()
                return ret
            except SQLAlchemyError as e:
                session.rollback()
                logging.getLogger("Transaction Middleware").warning(e)
                #raise e
        else:
            # db not configured yet, ignore transactions for now
            return next_callable(command)
