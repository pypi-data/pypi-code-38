from .request import request
from . import validator

__all__ = ['Task', ]


class Task:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def create(self, task):
        """
        task: {
            'name': str,
            'description': str,
            'status': str,
            'budget': str,
            'award': str,
            'numberOfParticipants': int,
            'startedAt': str,
            'endedAt': str,
            'projectId': int,  # 可选
        }
        """
        keys = [
            'name', 'description', 'status', 'budget', 'award',
            'numberOfParticipants', 'startedAt', 'endedAt',
        ]
        validator.check_dict_and_assert('task', task, keys)
        return request(
            self.config.host,
            method='POST',
            path='/tasks',
            data=task,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def update(self, task_id, task):
        """
        task_id: int
        task: {
            'name': str,
            'description': str,
            'status': str,
            'budget': str,
            'award': str,
            'numberOfParticipants': int,
            'startedAt': str,
            'endedAt': str,
            'projectId': int,  # 可选
        }
        """
        keys = [
            'name', 'description', 'status', 'budget', 'award',
            'numberOfParticipants', 'startedAt', 'endedAt',
        ]
        validator.check_dict_and_assert('task', task, keys)
        return request(
            self.config.host,
            method='PUT',
            path=f'/tasks/{task_id}',
            data=task,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )

    def remove(self, task_id):
        """
        :param task_id: int
        """
        request(
            self.config.host,
            method='DELETE',
            path=f'/tasks/{task_id}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )

    def get_tasks(self, project_id, _filter, _type, offset, limit):
        """
        :param project_id: int
        """
        validator.assert_exc(project_id, 'project_id cannot be null')
        query = {
            'projectId': project_id,
        }
        if _filter:
            query['filter'] = _filter
        if _type:
            query['type'] = _type
        if offset:
            query['offset'] = offset
        if limit:
            query['limit'] = limit
        return request(
            self.config.host,
            method='GET',
            path='/tasks',
            query=query,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )

    def get_summary(self, project_id):
        """
        :param project_id: int
        """
        validator.assert_exc(project_id, 'project_id cannot be null')
        query = {'projectId': project_id}
        return request(
            self.config.host,
            method='GET',
            path='/tasks/summary',
            query=query,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )

    def get_by_id(self, _id):
        """
        :param _id: int
        """
        validator.assert_exc(_id, '_id cannot be null')
        return request(
            self.config.host,
            method='GET',
            path=f'/tasks/{_id}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )
