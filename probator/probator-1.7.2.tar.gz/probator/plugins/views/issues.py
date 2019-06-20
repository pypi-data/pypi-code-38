import re
import shlex

from probator.constants import ROLE_USER, RGX_PROPERTY, HTTP
from probator.plugins import BaseView
from probator.plugins.types.issues import BaseIssue
from probator.utils import from_camelcase
from probator.wrappers import check_auth, rollback


class IssueGet(BaseView):
    URLS = ['/api/v1/issues/details/<string:issue_id>']

    @rollback
    @check_auth(ROLE_USER)
    def get(self, issue_id):
        issue = BaseIssue.get(issue_id)

        if issue:
            return self.make_response({
                'message': None,
                'issue': issue
            })
        else:
            return self.make_response({
                'message': 'Issue not found',
                'issue': None
            })


class IssueList(BaseView):
    URLS = ['/api/v1/issues']

    @rollback
    @check_auth(ROLE_USER)
    def get(self):
        self.reqparse.add_argument('limit', type=int, default=25)
        self.reqparse.add_argument('page', type=int, default=0)
        self.reqparse.add_argument('accounts', type=str, default=None, action='append')
        self.reqparse.add_argument('locations', type=str, default=None, action='append')
        self.reqparse.add_argument('issueTypes', dest='issue_types', type=str, default=None, action='append')
        self.reqparse.add_argument('terms', type=str, default=None)

        args = self.reqparse.parse_args()
        query = {
            'limit': args.limit
        }

        if args.accounts:
            query['accounts'] = args.accounts

        if args.locations:
            query['locations'] = args.locations

        properties = {}
        if args.terms:
            try:
                for keyword in shlex.split(args.terms):
                    if RGX_PROPERTY.match(keyword):
                        groups = RGX_PROPERTY.match(keyword).groupdict()

                        lx = shlex.shlex(groups['value'])
                        lx.whitespace = ['=']
                        lx.whitespace_split = True
                        name, values = list(lx)

                        vlx = shlex.shlex(re.sub(r'^"|"$', '', values))
                        vlx.whitespace = ['|']
                        vlx.whitespace_split = True
                        values = list(map(lambda x: int(x) if x.isnumeric() else x, list(vlx)))

                        properties[from_camelcase(name)] = values

            except ValueError:
                return self.make_response('Invalid formatted query', HTTP.BAD_REQUEST)

        if args.issue_types:
            query['issue_types'] = args.issue_types

        if args.page:
            query['page'] = args.page

        if properties:
            query['properties'] = properties

        total, issues = BaseIssue.find(**query)
        issues = [x.to_json() for x in issues]
        response = {
            'message': None,
            'issueCount': total,
            'issues': issues
        }

        return self.make_response(response)
