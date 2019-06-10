from dli.siren import siren_to_entity
from dli.client.utils import ensure_count_is_valid

"""Functions related to the current logged in user."""


class MeFunctions:

    @property
    def __root(self):
        return self.ctx.memoized(
            self.get_root_siren().me,
            "me_root"
        )

    def _get_my_entities(self, entity, my_entities_func, count):
        ensure_count_is_valid(count)

        result = my_entities_func(page_size=count)
        return result.get_entities(rel=entity)

    def get_my_packages(self, count=100):
        """
        Returns a list of packages where session user account is: a Manager, Tech Data Ops or Access Manager.

        :param int count: The number of items to retrieve, defaults to 100.

        :returns: List of my packages.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_packages = client.get_my_packages()

        """
        packages = self._get_my_entities('package', self.__root.my_packages, count)
        return [siren_to_entity(p) for p in packages]

    def get_my_consumed_packages(self, count=100):
        """
        Returns a list of all the packages user session account has access to.

        :param int count: The number of items to retrieve, defaults to 100.

        :returns: List of my consumed packages.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_consumed_packages = client.get_my_consumed_packages()

        """
        access_requests = self._get_my_entities('access_request', self.__root.list_consumed_packages, count)
        return [siren_to_entity(r.package()) for r in access_requests]

    def get_my_collections(self, count=100):
        """
        Returns a list of collections where session user account is the manager.

        :param int count: The number of items to retrieve, defaults to 100.

        :returns: List of my collections.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_collections = client.get_my_collections()

        """
        collections = self._get_my_entities('collection', self.__root.my_collections, count)
        return [siren_to_entity(c) for c in collections]

    def get_my_accounts(self):
        """
        Returns a list of all the accounts associated with user session.

        :returns: list of all associated accounts.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_accounts = client.get_my_accounts()

        """
        result = self.get_root_siren().list_my_accounts()
        accounts = result.get_entities(rel="")
        return [siren_to_entity(a) for a in accounts]
