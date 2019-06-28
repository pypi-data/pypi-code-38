from tsuru.models.base import BaseModel


class App(BaseModel):
    _RESOURCE_NAME = 'apps'
    _PK_FIELD = 'name'

    @property
    def name(self):
        return self._get('name')

    @property
    def pool(self):
        return self._get('pool')

    @property
    def team_owner(self):
        return self._get('team_owner')

    @property
    def owner(self):
        return self._get('owner')

    @property
    def platform(self):
        return self._get('platform')

    @property
    def repository(self):
        return self._get('repository')

    @property
    def router(self):
        return self._get('router')

    @property
    def teams(self):
        from tsuru import Team

        yield from [Team(data={'name': name}) for name in self._get('team')]

    @property
    def ip(self):
        return self._get('ip')

    @property
    def cnames(self):
        return self._get('cname')

    @property
    def deploys_amount(self):
        return self._get('deploys')

    @property
    def description(self):
        return self._get('description')

    @property
    def lock(self):
        from tsuru import Lock

        lock_data = self._get('lock')
        return Lock(data=lock_data)

    @property
    def plan(self):
        from tsuru import Plan

        plan_data = self._get('plan')
        return Plan(data=plan_data)

    @property
    def envs(self):
        from tsuru import Env

        yield from self._bound_list(resource_class=Env)

    def get_logs(self, lines=10):
        from tsuru import Log

        yield from self._bound_list(resource_class=Log, params={'lines': lines})

    @property
    def units(self):
        yield from self._get('units')

    def get_unit(self, pk):
        from tsuru import Unit

        return self._bound_detail(
            resource_class=Unit,
            pk=pk,
        )
