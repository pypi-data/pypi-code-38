from probator.constants import ROLE_ADMIN
from probator.database import db
from probator.plugins import BaseView
from probator.schema import AuditLog
from probator.wrappers import rollback, check_auth
from sqlalchemy import distinct


class AuditLogList(BaseView):
    URLS = ['/api/v1/auditlog']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self):
        self.reqparse.add_argument('page', type=int, default=0)
        self.reqparse.add_argument('count', type=int, default=25)
        args = self.reqparse.parse_args()

        qry = db.AuditLog.order_by(AuditLog.audit_log_event_id.desc())

        total_events = qry.count()
        qry = qry.limit(args.count)

        if args.page > 0:
            offset = args.page * args.count
            qry = qry.offset(offset)

        return self.make_response({
            'auditLogEvents': qry.all(),
            'auditLogEventCount': total_events,
            'eventTypes': [x[0] for x in db.query(distinct(AuditLog.event)).all()]
        })


class AuditLogGet(BaseView):
    URLS = ['/api/v1/auditlog/<int:audit_log_event_id>']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self, audit_log_event_id):
        event = db.AuditLog.find_one(AuditLog.audit_log_event_id == audit_log_event_id)

        return self.make_response({
            'auditLogEvent': event
        })
