from tsuru import exceptions
from tsuru.models.base import BaseModel


class Team(BaseModel):
    _RESOURCE_NAME = 'teams'
    _PK_FIELD = 'name'

    @classmethod
    def get(cls, pk):
        # Since /teams endpoint does not support detail,
        # we fetch-all-and-match
        all_teams = cls.list()
        for team in all_teams:
            if team.pk == pk:
                return team
        raise exceptions.DoesNotExist()

    @property
    def name(self):
        return self._get('name')

    @property
    def permissions(self):
        return self._get('permissions')
