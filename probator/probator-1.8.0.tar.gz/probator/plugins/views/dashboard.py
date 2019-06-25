from flask import current_app, session
from more_itertools import first
from munch import munchify
from sqlalchemy import func
from werkzeug.local import LocalProxy

from probator import PROBATOR_PLUGINS
from probator.config import dbconfig
from probator.constants import ROLE_USER, PLUGIN_NAMESPACES
from probator.database import db
from probator.plugins import BaseView
from probator.schema import IssueModel, Resource, Account
from probator.utils import limit_value
from probator.wrappers import rollback, check_auth

__AUDITED_RESOURCES = None
SUPPORTED_RESOURCES = munchify({
    'auditor_required_tags': {
        'key': 'audit_scopes',
        'type': 'choice'
    },
    'auditor_encryption': {
        'key': 'audited_resources',
        'type': 'choice'
    }
})


def get_issue_resource_types():
    global __AUDITED_RESOURCES

    if __AUDITED_RESOURCES is None:
        __AUDITED_RESOURCES = set()
        auditors = PROBATOR_PLUGINS[PLUGIN_NAMESPACES['auditor']].get('plugins', [])
        types = {v.resource_type: k for k, v in current_app.types.items()}

        for ep in auditors:
            if ep.name in SUPPORTED_RESOURCES:
                metadata = SUPPORTED_RESOURCES[ep.name]
                cls = ep.load()
                if not cls.enabled():
                    continue

                cfg_item = dbconfig.get(key=metadata.key, namespace=cls.ns)

                if metadata.type == 'choice':
                    for item in cfg_item['enabled']:
                        resource_type = types.get(item)
                        if resource_type:
                            __AUDITED_RESOURCES.add(resource_type)

                elif metadata.type == 'list':
                    for item in cfg_item:
                        resource_type = types.get(item)
                        if resource_type:
                            __AUDITED_RESOURCES.add(resource_type)

                else:
                    raise TypeError(f'Unsupported config item type for dashboard: {metadata.type}')

    return __AUDITED_RESOURCES


ISSUE_RESOURCE_TYPES = LocalProxy(get_issue_resource_types)


class Dashboard(BaseView):
    URLS = ['/api/v1/dashboard']

    @rollback
    @check_auth(ROLE_USER)
    def get(self):
        """Return stats for all the accounts

        Returns:
            `Response`
        """
        resources = db.query(
            Resource.resource_type_id, func.count(Resource.resource_id).label('count')
        ).group_by(
            Resource.resource_type_id
        ).all()

        issues = db.query(
            IssueModel.issue_type_id, func.count(IssueModel.issue_id).label('count')
        ).group_by(
            IssueModel.issue_type_id
        ).all()

        resource_count = first(db.query(func.count(Resource.resource_id)).first())
        issue_count = first(db.query(func.count(IssueModel.issue_id)).first())

        return self.make_response({
            'resources': [
                {
                    'resourceTypeId': row.resource_type_id,
                    'count': row.count
                } for row in resources
            ],
            'issues': [
                {
                    'issueTypeId': row.issue_type_id,
                    'count': row.count
                } for row in issues
            ],
            'resourceCount': resource_count,
            'issueCount': issue_count,
            'issueSummary': self._get_compliance_stats()
        })

    @staticmethod
    def _get_compliance_stats():
        """Return compliance level statistics for each account

        Returns:
            `dict`
        """
        resource_sq = db.query(
            Resource.account_id, func.count(Resource.resource_id).label('resource_count')
        ).filter(
            Resource.resource_type_id.in_(ISSUE_RESOURCE_TYPES),
            Resource.account_id.in_(session['accounts']),
        ).group_by(
            Resource.account_id
        ).subquery()

        issues_sq = db.query(
            IssueModel.account_id, func.count(IssueModel.issue_id).label('issue_count')
        ).group_by(
            IssueModel.account_id
        ).subquery()

        qry = db.query(
            Account.account_id, resource_sq.c.resource_count, issues_sq.c.issue_count
        ).outerjoin(
            resource_sq, Account.account_id == resource_sq.c.account_id
        ).outerjoin(
            issues_sq, Account.account_id == issues_sq.c.account_id
        ).filter(
            Account.account_id.in_(session['accounts']),
            Account.enabled == 1
        )

        out = {}
        for row in qry.all():
            issue_count = row.issue_count or 0
            resource_count = row.resource_count or 0
            if resource_count:
                percent = limit_value(value=100 - ((issue_count / resource_count) * 100), min_value=0, max_value=100)
            else:
                percent = 100

            out[row.account_id] = {
                'issueCount': issue_count,
                'resourceCount': row.resource_count,
                'percentage': percent
            }

        return out
