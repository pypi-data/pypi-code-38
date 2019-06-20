from datetime import datetime, timedelta

from flask import session
from probator.constants import ROLE_ADMIN
from probator.database import db
from probator.log import auditlog
from probator.plugins import BaseView
from probator.schema import LogEvent
from probator.wrappers import check_auth, rollback
from sqlalchemy import func, desc


class Logs(BaseView):
    URLS = ['/api/v1/logs']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self):
        self.reqparse.add_argument('count', type=int, default=25)
        self.reqparse.add_argument('page', type=int, default=0)
        self.reqparse.add_argument('levelno', type=int, default=0)
        args = self.reqparse.parse_args()

        if args.levelno > 0:
            total_events = db.query(
                func.count(LogEvent.log_event_id)
            ).filter(LogEvent.levelno >= args.levelno).first()[0]

            qry = (
                db.LogEvent
                .filter(LogEvent.levelno >= args.levelno)
                .order_by(desc(LogEvent.timestamp))
                .limit(args.count)
            )
        else:
            total_events = db.query(func.count(LogEvent.log_event_id)).first()[0]
            qry = (
                db.LogEvent
                .order_by(desc(LogEvent.timestamp))
                .limit(args.count)
            )

        if args.page > 0:
            offset = args.page * args.count
            qry = qry.offset(offset)

        events = qry.all()
        return self.make_response({
            'logEventCount': total_events,
            'logEvents': events
        })

    @rollback
    @check_auth(ROLE_ADMIN)
    def delete(self):
        self.reqparse.add_argument('maxAge', dest='max_age', type=int, default=31)
        args = self.reqparse.parse_args()

        db.LogEvent.filter(
            func.datesub(
                LogEvent.timestamp < datetime.now() - timedelta(days=args.max_age)
            )
        ).delete()

        db.session.commit()
        auditlog(event='logs.prune', actor=session['user'].username, data=args)

        return self.make_response(f'Pruned logs older than {args.max_age} days')


class LogDetails(BaseView):
    URLS = ['/api/v1/logs/<int:log_event_id>']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self, log_event_id):
        evt = db.LogEvent.find_one(LogEvent.log_event_id == log_event_id)

        return self.make_response({'logEvent': evt})
