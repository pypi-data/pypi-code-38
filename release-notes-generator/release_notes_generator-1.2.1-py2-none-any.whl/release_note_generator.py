import services


class ReleaseNoteGenerator(object):
    DEFAULT_URL = 'https://github.counsyl.com/api/graphql'

    def __init__(self,
                 token,
                 pr_nums,
                 client=services.GraphQLClient,
                 url=DEFAULT_URL,
                 repository_name='auto_pipeline',
                 pr_fetcher=services.PRFetcher,
                 notes_parser=services.ReleaseNotesParser):

        self.client = client(url)
        self.client.inject_token(token)
        self.token = token
        self.repository_name = repository_name
        self.pr_nums = pr_nums
        self.pr_fetcher = pr_fetcher(self.client)
        self.notes_parser = notes_parser

    def release_notes(self):
        pr_descriptions = self.pr_fetcher.fetch_pr_descriptions(
            self.pr_nums, repository_name=self.repository_name)
        return self.notes_parser(pr_descriptions).parse_release_notes()
