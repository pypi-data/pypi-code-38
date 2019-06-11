from .request import request
from . import validator

__all__ = ['Draft', ]


class Draft:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def create(self, draft):
        """
        :param draft: dict
            {
                'title', str,
                'content': str,
                'mime_type': str,
                'source': str,
                'origin_url': str,
                'project_id': str
            }
        """
        keys = ['title', 'content', 'mime_type', ]
        validator.check_dict_and_assert('draft', draft, keys)
        auth_opts = self.config.get_auth_opts()
        data = {
            'title': draft['title'],
            'content': draft['content'],
            'mimeType': draft['mime_type'],
        }
        if draft.get('source'):
            data['source'] = draft['source']
        if draft.get('origin_url'):
            data['originUrl'] = draft['origin_url']
        if draft.get('project_id'):
            data['projectId'] = draft['project_id']
        return request(
            self.config.host,
            method='POST',
            path='/drafts',
            data=data,
            auth_opts=auth_opts,
            debug=self.config.debug,
        )

    def update(self, _id, draft):
        """
        :param _id: str, draft id
        :param draft: dict
            {
                'title', str,
                'content': str,
                'mime_type': str,
                'source': str,
                'origin_url': str,
                'project_id': str
            }
        """
        validator.assert_exc(_id, '_id cannot be null')
        keys = ['title', 'content', 'mime_type', ]
        validator.check_dict_and_assert('draft', draft, keys)
        auth_opts = self.config.get_auth_opts()
        data = {
            'title': draft['title'],
            'content': draft['content'],
            'mimeType': draft['mime_type'],
        }
        if draft.get('source'):
            data['source'] = draft['source']
        if draft.get('origin_url'):
            data['originUrl'] = draft['origin_url']
        if draft.get('project_id'):
            data['projectId'] = draft['project_id']
        return request(
            self.config.host,
            method='PUT',
            path=f'/drafts/{_id}',
            data=data,
            auth_opts=auth_opts,
            debug=self.config.debug,
        )

    def delete(self, _id):
        """
        :param _id: str, draft id
        """
        validator.assert_exc(_id, '_id cannot be null')
        return request(
            self.config.host,
            method='DELETE',
            path=f'/drafts/{_id}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_by_id(self, _id):
        """
        :param _id: str, draft id
        """
        validator.assert_exc(_id, '_id cannot be null')
        return request(
            self.config.host,
            method='GET',
            path=f'/drafts/{_id}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_drafts(self):
        return request(
            self.config.host,
            method='GET',
            path='/drafts',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )
