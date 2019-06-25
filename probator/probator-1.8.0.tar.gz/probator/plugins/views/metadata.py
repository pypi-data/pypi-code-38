from flask import session, current_app

from probator import AWS_REGIONS, PROBATOR_PLUGINS, __version__ as api_version
from probator.constants import ROLE_USER, PLUGIN_NAMESPACES, ROLE_ADMIN
from probator.plugins import BaseView
from probator.plugins.types.accounts import BaseAccount
from probator.utils import to_camelcase
from probator.wrappers import check_auth, rollback


class MetaData(BaseView):
    URLS = ['/api/v1/metadata']

    @rollback
    @check_auth(ROLE_USER)
    def get(self):
        _, accounts = BaseAccount.search(account_ids=session['accounts'])
        accounts = [acct.to_json(is_admin=ROLE_ADMIN in session['user'].roles) for acct in accounts]
        account_types = list(self.__get_account_types())
        resource_types = list(self.__get_resource_types())
        issue_types = list(self.__get_issue_types())

        return self.make_response({
            'accounts': accounts,
            'regions': list(AWS_REGIONS),
            'accountTypes': account_types,
            'resourceTypes': resource_types,
            'issueTypes': issue_types,
            'currentUser': session['user'].to_json(),
            'notifiers': [{'type': k, 'validation': v} for k, v in current_app.notifiers.items()],
            'apiVersion': api_version
        })

    @staticmethod
    def __get_account_types():
        for entry_point in PROBATOR_PLUGINS[PLUGIN_NAMESPACES['accounts']]['plugins']:
            cls = entry_point.load()
            yield {
                'name': cls.account_type,
                'properties': [
                    {key: to_camelcase(value) if key == 'key' else value for key, value in prop.to_dict().items()}
                    for prop in cls.class_properties
                ]
            }

    @staticmethod
    def __get_resource_types():
        for type_id, cls in current_app.types.items():
            properties = []
            for prop in cls.resource_properties:
                properties.append({
                    'key': to_camelcase(prop.key),
                    'name': prop.name,
                    'type': prop.type,
                    'show': prop.show,
                    'primary': prop.primary,
                    'resourceReference': prop.resource_reference
                })

            yield {
                'name': cls.resource_name,
                'resourceGroup': cls.resource_group,
                'resourceTypeId': type_id,
                'resourceType': cls.resource_type,
                'properties': properties
            }

    @staticmethod
    def __get_issue_types():
        for type_id, cls in current_app.issue_types.items():
            properties = []
            for prop in cls.issue_properties:
                properties.append({
                    'key': to_camelcase(prop.key),
                    'name': prop.name,
                    'type': prop.type,
                    'show': prop.show,
                    'primary': prop.primary,
                    'resourceReference': prop.resource_reference,
                    'accountReference': prop.account_reference
                })

            yield {
                'name': cls.issue_name,
                'issueTypeId': type_id,
                'issueType': cls.issue_type,
                'properties': properties
            }
