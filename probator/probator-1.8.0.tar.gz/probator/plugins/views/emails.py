from flask import session
from probator.constants import ROLE_ADMIN, HTTP
from probator.database import db
from probator.exceptions import EmailSendError
from probator.log import auditlog
from probator.plugins import BaseView
from probator.schema import Email
from probator.utils import send_notification, NotificationContact
from probator.wrappers import check_auth, rollback
from sqlalchemy import desc, func, distinct


class EmailList(BaseView):
    URLS = ['/api/v1/emails']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self):
        self.reqparse.add_argument('page', type=int, default=1)
        self.reqparse.add_argument('count', type=int, default=100)
        self.reqparse.add_argument('subsystems', type=str, default=None, action='append')
        args = self.reqparse.parse_args()

        total_qry = db.query(func.count(Email.email_id))
        qry = db.Email.order_by(desc(Email.timestamp))

        if args.subsystems:
            subsystems = [x for x in map(lambda x: x.lower(), args.subsystems)]
            qry = qry.filter(func.lower(Email.subsystem).in_(subsystems))
            total_qry = total_qry.filter(func.lower(Email.subsystem).in_(subsystems))

        if args.page > 0:
            offset = args.page * args.count
            qry = qry.offset(offset)

        qry = qry.limit(args.count)
        emails = qry.all()
        total_emails = total_qry.first()[0]

        return self.make_response({
            'message': None,
            'emailCount': total_emails,
            'emails': emails,
            'subsystems': [x[0] for x in db.query(distinct(Email.subsystem)).all()]
        })


class EmailGet(BaseView):
    URLS = ['/api/v1/emails/<int:email_id>']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self, email_id):
        email = db.Email.find_one(Email.email_id == email_id)

        if not email:
            return self.make_response({
                'message': 'Email not found',
                'email': None
            })

        return self.make_response({
            'email': email.to_json(True)
        })

    @rollback
    @check_auth(ROLE_ADMIN)
    def put(self, email_id):
        email = db.Email.find_one(Email.email_id == email_id)
        if not email:
            return self.make_response({
                'message': 'Email not found',
                'email': None
            })

        try:
            if type(email.recipients) == list:
                recipients = [NotificationContact('email', x) for x in email.recipients]
            elif type(email.recipients) == str:
                recipients = [NotificationContact('email', email.recipients)]
            else:
                return self.make_response('Unable to determine recipients', HTTP.SERVER_ERROR)

            send_notification(
                subsystem=email.subsystem,
                recipients=recipients,
                subject=email.subject,
                body_html=email.message_html,
                body_text=email.message_text
            )

            auditlog(event='email.resend', actor=session['user'].username, data={'emailId': email_id})
            return self.make_response('Email resent successfully')

        except EmailSendError as ex:
            self.log.exception(f'Failed resending email {email.email_id}: {ex}')
            return self.make_response(f'Failed resending the email: {ex}', HTTP.UNAVAILABLE)
