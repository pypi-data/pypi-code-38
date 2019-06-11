from dli.siren import siren_to_entity
from dli.client.utils import ensure_count_is_valid


class SearchFunctions:
    """
    Catalogue search functions.
    """

    @property
    def __root(self):
        return self.ctx.memoized(self.get_root_siren)

    def _search_my_entities(self, entity, search_func, term, count):
        ensure_count_is_valid(count)

        # replicating UI behavior, for empty term we want an empty search
        if term is None or term == "":
            return []

        result = search_func(query=term, page_size=count)
        return result.get_entities(rel=entity)

    def search(self, term, count=100):
        """
        Search across all catalogue entities given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned.

        :returns: A list of Catalogue entities
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                automotive_catalogue_entities = client.search(
                    term="Automotive",
                    count=100
                )

        """
        results = self._search_my_entities("", self.__root.search, term, count)
        return [siren_to_entity(e) for e in results]

    def search_packages(self, term, count=100):
        """
        Search across packages in the catalogue given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned. Defaults to 100.

        :returns: A list of packages
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                automotive_packages = client.search_packages(
                    term="Automotive",
                    count=100
                )

        """
        packages = self._search_my_entities("package", self.__root.search_packages, term, count)
        return [siren_to_entity(p) for p in packages]

    def search_collections(self, term, count=100):
        """
        Search across collections in the catalogue given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned. Defaults to 100.

        :returns: A list of collections
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                automotive_collections = client.search_collections(
                    term="Automotive",
                    count=100
                )

        """
        collections = self._search_my_entities("collection", self.__root.search_collections, term, count)
        return [siren_to_entity(c) for c in collections]

    def search_datasets(self, term, count=100):
        """
        Search across datasets in the catalogue given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned. Defaults to 100.

        :returns: A list of datasets
        :rtype: list[dataset.namedtuple]

        - **Sample**

        .. code-block:: python

                results = client.search_datasets(
                    term="CDS",
                    count=100
                )

        """
        datasets = self._search_my_entities("dataset", self.__root.search_datasets, term, count)
        return [siren_to_entity(c) for c in datasets]
