from typing import List

from vk import API


from pyvko.api_based import ApiBased
from pyvko.pyvko import Group


class User(ApiBased):
    def __init__(self, api: API, user_id: int = 0) -> None:
        super().__init__(api)

        self.id = user_id

    def groups(self) -> List[Group]:
        groups_response = self.api.groups.get(user_id=self.id, v=5.92, extended=1)

        groups_objects = groups_response["items"]

        groups = [Group(api=self.api, group_object=group_object) for group_object in groups_objects]

        return groups
