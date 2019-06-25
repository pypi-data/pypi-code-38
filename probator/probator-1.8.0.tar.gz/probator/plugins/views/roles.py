from flask import session

from probator.constants import ROLE_ADMIN, HTTP
from probator.database import db
from probator.log import auditlog
from probator.plugins import BaseView
from probator.schema import Role
from probator.wrappers import check_auth, rollback


class RoleList(BaseView):
    URLS = ['/api/v1/roles']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self):
        roles = db.Role.all()

        return self.make_response({
            'roles': roles,
            'roleCount': len(roles)
        })

    @rollback
    @check_auth(ROLE_ADMIN)
    def post(self):
        """Create a new role"""
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('color', type=str, required=True)
        args = self.reqparse.parse_args()

        role = Role()
        role.name = args.name
        role.color = args.color

        db.session.add(role)
        db.session.commit()
        auditlog(event='role.create', actor=session['user'].username, data=args)

        return self.make_response(f'Role {role.name} (ID: {role.role_id}) has been created', HTTP.CREATED)


class RoleGet(BaseView):
    URLS = ['/api/v1/role/<int:role_id>']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self, role_id):
        """Get a specific role information"""
        role = db.Role.find_one(Role.role_id == role_id)

        if not role:
            return self.make_response('No such role found', HTTP.NOT_FOUND)

        return self.make_response({'role': role})

    @rollback
    @check_auth(ROLE_ADMIN)
    def put(self, role_id):
        """Update a user role"""
        self.reqparse.add_argument('color', type=str, required=True)
        args = self.reqparse.parse_args()

        role = db.Role.find_one(Role.role_id == role_id)
        if not role:
            self.make_response({
                'message': 'No such role found'
            }, HTTP.NOT_FOUND)

        role.color = args.color

        db.session.add(role)
        db.session.commit()
        auditlog(event='role.update', actor=session['user'].username, data=args)

        return self.make_response(f'Role {role.name} has been updated')

    @rollback
    @check_auth(ROLE_ADMIN)
    def delete(self, role_id):
        """Delete a user role"""
        role = db.Role.find_one(Role.role_id == role_id)
        if not role:
            return self.make_response('No such role found', HTTP.NOT_FOUND)

        if role.name in ('User', 'Admin'):
            return self.make_response('Cannot delete the built-in roles', HTTP.BAD_REQUEST)

        db.session.delete(role)
        db.session.commit()
        auditlog(event='role.delete', actor=session['user'].username, data={'roleId': role_id})

        return self.make_response({
            'message': 'Role has been deleted',
            'roleId': role_id
        })
