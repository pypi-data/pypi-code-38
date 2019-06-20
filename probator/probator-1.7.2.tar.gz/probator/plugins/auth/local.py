from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from flask import session, request

from probator.constants import MSG_INVALID_USER_OR_PASSWORD, ROLE_ADMIN, ROLE_USER
from probator.database import db
from probator.plugins import BaseAuthPlugin, BaseView
from probator.schema import Role, User
from probator.utils import generate_csrf_token, generate_jwt_token, generate_password, hash_password

ph = PasswordHasher()


class BaseLocalAuthView(BaseView):
    name = 'Local Authentication'
    ns = 'auth_local'


class LocalAuthLogin(BaseLocalAuthView):
    URLS = ['/auth/local/login']

    def post(self):
        self.reqparse.add_argument('username', type=str, required=True)
        self.reqparse.add_argument('password', type=str, required=True)
        args = self.reqparse.parse_args()

        try:
            user = db.User.filter(
                User.username == args['username'],
                User.auth_system == self.name
            ).first()

            if not user:
                self.log.warn(f'Authentication attemp for unknown user {args.username} from {request.remote_addr}')
                return self.make_response(MSG_INVALID_USER_OR_PASSWORD, 400)

            ph.verify(user.password, args['password'])

            # Setup the user session with all the information required
            session['user'] = user
            session['csrf_token'] = generate_csrf_token()
            session['accounts'] = [x.account_id for x in db.Account.all() if x.user_has_access(user)]

            token = generate_jwt_token(user, self.name)

            return self.make_response({
                'authToken': token,
                'csrfToken': session['csrf_token']
            }, 200)

        except VerificationError:
            self.log.warn(f'Failed verifying password for {args.username} from {request.remote_addr}')
            return self.make_response(MSG_INVALID_USER_OR_PASSWORD, 400)

        except Exception as ex:
            self.log.exception(f'Unknown error occured while attempting to login user {args.username} from {request.remote_addr}: {ex}')

        finally:
            db.session.rollback()


class LocalAuthLogout(BaseLocalAuthView):
    URLS = ['/auth/local/logout']

    def get(self):
        pass


class LocalAuth(BaseAuthPlugin):
    name = 'Local Authentication'
    ns = 'auth_local'
    views = (LocalAuthLogin, LocalAuthLogout)
    readonly = False
    login = {'state': 'auth.login'}
    logout = '/auth/local/logout'

    def bootstrap(self):
        admin_user = db.User.find_one(
            User.username == 'admin',
            User.auth_system == self.name
        )

        if not admin_user:
            roles = db.Role.filter(Role.name.in_((ROLE_ADMIN, ROLE_USER))).all()
            admin_password = generate_password()
            admin_user = User()

            admin_user.username = 'admin'
            admin_user.name = 'Administrator'
            admin_user.auth_system = self.name
            admin_user.password = hash_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            db.session.refresh(admin_user)
            User.add_role(admin_user, roles)

            self.log.error(f'Created admin account for local authentication, username: admin, password: {admin_password}')
