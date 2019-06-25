from collections.abc import Sized, Iterator


class ResponsePaginator(Sized, Iterator):
    """
    A lazy generator to handle paginated Arkindex API endpoints.
    Does not perform any requests to the API until it is required.
    """

    def __init__(self, client, *request_args, **request_kwargs):
        r"""
        :param client apistar.Client: An API client to use to perform requests for each page.
        :param \*request_args: Arguments to send to :meth:`apistar.Client.request`.
        :param \**request_kwargs: Keyword arguments to send to :meth:`apistar.Client.request`.
        """
        self.client = client
        """The APIStar client used to perform requests on each page."""

        self.data = {}
        """Stored data from the last performed request."""

        self.results = []
        """Stored results from the last performed request."""

        self.request_args = request_args
        """Arguments to send to :meth:`apistar.Client.request` with each request."""

        self.request_kwargs = request_kwargs
        """
        Keyword arguments to send to :meth:`apistar.Client.request` with each request.
        ``page`` is overriden to set the page number.
        """

        self.current_page = 0
        """The current page number. 0 if no pages have been requested yet."""

    def _fetch_page(self, page):
        self.request_kwargs['page'] = page
        self.data = self.client.request(*self.request_args, **self.request_kwargs)
        self.results = self.data.get('results', [])
        self.current_page = page

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.results) < 1:
            if self.data and self.data.get('next') is None:
                raise StopIteration
            self._fetch_page(self.current_page + 1)

        # Even after fetching a new page, if the new page is empty, just fail
        if len(self.results) < 1:
            raise StopIteration

        return self.results.pop(0)

    def __len__(self):
        # Handle calls to len when no requests have been made yet
        if not self.data and self.current_page < 1:
            self._fetch_page(1)
        return self.data['count']

    def __repr__(self):
        return '<{} via {!r}: {!r} {!r}>'.format(
            self.__class__.__name__,
            self.client,
            self.request_args,
            self.request_kwargs,
        )
