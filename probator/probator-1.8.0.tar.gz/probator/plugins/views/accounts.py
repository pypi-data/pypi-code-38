import json
import re
from base64 import b64encode

from flask import session, Response, current_app
from flask_restful import inputs
from munch import munchify
from probator import get_plugin_by_name
from probator.constants import ROLE_ADMIN, HTTP, ROLE_USER, AccountTypes, PLUGIN_NAMESPACES
from probator.database import db
from probator.exceptions import ProbatorError, AccountException
from probator.json_utils import ProbatorJSONEncoder, ProbatorJSONDecoder
from probator.log import auditlog
from probator.plugins import BaseView
from probator.plugins.types.accounts import BaseAccount
from probator.schema import AccountType
from probator.utils import from_camelcase, to_camelcase
from probator.wrappers import rollback, check_auth


def validate_contacts(contacts):
    for contact in munchify(contacts):
        if contact.type in current_app.notifiers:
            if not re.match(current_app.notifiers[contact.type], contact.value, re.I):
                raise Exception(f'Invalid formatted contact for {contact.type}: {contact.value}')

        else:
            raise Exception(f'Unsupported notification type: {contact.type}')


class AccountList(BaseView):
    URLS = ['/api/v1/account']

    @rollback
    @check_auth(ROLE_USER)
    def get(self):
        """List all accounts"""
        _, accounts = BaseAccount.search()

        if ROLE_ADMIN not in session['user'].roles:
            accounts = list(filter(lambda acct: acct.account_id in session['accounts'], accounts))

        return self.make_response({
            'message': None,
            'accounts': [x.to_json(is_admin=ROLE_ADMIN in session['user'].roles or False) for x in accounts]
        })

    @rollback
    @check_auth(ROLE_ADMIN)
    def post(self):
        """Create a new account"""
        self.reqparse.add_argument('accountName', type=str, required=True)
        self.reqparse.add_argument('accountType', type=str, required=True)
        self.reqparse.add_argument('contacts', type=dict, required=True, action='append')
        self.reqparse.add_argument('enabled', type=inputs.boolean, required=True, default=True)
        self.reqparse.add_argument('requiredGroups', type=str, action='append', default=())
        self.reqparse.add_argument('properties', type=dict, required=True)
        args = self.reqparse.parse_args()

        account_class = get_plugin_by_name(PLUGIN_NAMESPACES['accounts'], args.accountType)
        if not account_class:
            raise ProbatorError(f'Invalid account type: {args.accountType}')

        validate_contacts(args.contacts)

        for key in ('accountName', 'accountType', 'contacts', 'enabled'):
            try:
                self.__validate_input(args[key])

            except ValueError as ex:
                raise ValueError(f'{ex} for {key}')

        class_properties = {from_camelcase(key): value for key, value in args.properties.items()}
        for prop in account_class.class_properties:
            if prop.key not in class_properties:
                raise ProbatorError(f'Missing required property {prop.name}')

        acct = account_class.create(
            account_name=args.accountName,
            contacts=args.contacts,
            enabled=args.enabled,
            required_roles=args.requiredGroups,
            properties=class_properties,
            auto_commit=False
        )
        db.session.commit()

        # Add the newly created account to the session so we can see it right away
        session['accounts'].append(acct.account_id)
        auditlog(event='account.create', actor=session['user'].username, data=args)

        return self.make_response({'message': 'Account created', 'accountId': acct.account_id}, HTTP.CREATED)

    @staticmethod
    def __validate_input(value):
        input_type = type(value)

        if input_type not in (int, tuple, list, str, bool):
            raise ValueError(f'Invalid or empty input type {input_type.__name__}')

        if input_type == bool:
            return True

        if input_type == str:
            value = value.strip()

        if value:
            return True


class AccountDetail(BaseView):
    URLS = ['/api/v1/account/<int:account_id>']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self, account_id):
        """Fetch a single account"""
        account = BaseAccount.get(account_id)
        if account:
            return self.make_response({
                'message': None,
                'account': account.to_json(is_admin=True)
            })
        else:
            return self.make_response({
                'message': 'Unable to find account',
                'account': None
            })

    @rollback
    @check_auth(ROLE_ADMIN)
    def put(self, account_id):
        """Update an account"""
        self.reqparse.add_argument('accountName', type=str, required=True)
        self.reqparse.add_argument('accountType', type=str, required=True)
        self.reqparse.add_argument('contacts', type=dict, required=True, action='append')
        self.reqparse.add_argument('enabled', type=inputs.boolean, required=True, default=False)
        self.reqparse.add_argument('requiredRoles', type=str, action='append', default=())
        self.reqparse.add_argument('properties', type=dict, required=True)
        args = self.reqparse.parse_args()

        account_class = get_plugin_by_name(PLUGIN_NAMESPACES['accounts'], args.accountType)
        if not account_class:
            raise ProbatorError(f'Invalid account type: {args.accountType}')

        validate_contacts(args.contacts)

        if not args.accountName.strip():
            raise Exception('You must provide an account name')

        if not args.contacts:
            raise Exception('You must provide at least one contact')

        class_properties = {from_camelcase(key): value for key, value in args.properties.items()}
        for prop in account_class.class_properties:
            if prop.key not in class_properties:
                raise ProbatorError(f'Missing required property {prop.name}')

        account = account_class.get(account_id)
        if account.account_type != args.accountType:
            raise ProbatorError('You cannot change the type of an account')

        account.account_name = args.accountName
        account.contacts = args.contacts
        account.enabled = args.enabled
        account.required_roles = args.requiredRoles
        account.update(**args.properties)
        account.save()

        auditlog(event='account.update', actor=session['user'].username, data=args)

        return self.make_response({'message': 'Account updated', 'account': account.to_json(is_admin=True)})

    @rollback
    @check_auth(ROLE_ADMIN)
    def delete(self, account_id):
        """Delete an account"""
        acct = BaseAccount.get(account_id)
        if not acct:
            raise Exception('No such account found')

        acct.delete()
        auditlog(event='account.delete', actor=session['user'].username, data={'accountId': account_id})

        return self.make_response('Account deleted')


class AccountImportExport(BaseView):
    URLS = ['/api/v1/account/imex']

    @rollback
    @check_auth(ROLE_ADMIN)
    def get(self):
        _, accounts = BaseAccount.search(include_disabled=True)
        out = [account.to_json(is_admin=True) for account in accounts]

        auditlog(event='account.export', actor=session['user'].username, data={})
        return Response(
            response=b64encode(
                bytes(
                    json.dumps(out, cls=ProbatorJSONEncoder),
                    'utf-8'
                )
            ),
            status=HTTP.OK
        )

    @rollback
    @check_auth(ROLE_ADMIN)
    def post(self):
        self.reqparse.add_argument('accounts', type=str, required=True)
        args = self.reqparse.parse_args()

        try:
            accounts = munchify(json.loads(args.accounts, cls=ProbatorJSONDecoder))

            for account_data in accounts:
                if not getattr(AccountTypes, account_data.accountType, None):
                    return self.make_response(f'Unsupported account type: {account_data.accountType}', HTTP.BAD_REQUEST)

                acct_type = AccountType.get(account_data.accountType)
                account_class = get_plugin_by_name(PLUGIN_NAMESPACES['accounts'], acct_type.account_type)
                acct = BaseAccount.get(account_data.accountName)
                if not acct:
                    acct = BaseAccount.create(
                        account_name=account_data.accountName,
                        contacts=account_data.contacts,
                        enabled=account_data.enabled,
                        properties=account_data.properties,
                        account_type_id=acct_type.account_type_id
                    )
                    db.session.add(acct)
                else:
                    acct.contacts = account_data.contacts
                    acct.enabled = account_data.enabled

                    for prop in account_class.class_properties:
                        key = to_camelcase(prop.key)
                        if key not in account_data.properties:
                            raise AccountException(f'Missing account attribute: {key}')

                        acct.set_property(from_camelcase(key), account_data.properties[key])

            db.session.commit()
            auditlog(event='account.import', actor=session['user'].username, data=accounts)

            return self.make_response('Accounts imported')
        except Exception as ex:
            self.log.exception('Failed importing accounts')

            return self.make_response(f'Error importing account data: {ex}', HTTP.SERVER_ERROR)
