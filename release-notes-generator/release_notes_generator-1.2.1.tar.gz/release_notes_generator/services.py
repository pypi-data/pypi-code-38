# Graphql
# https://developer.github.com/enterprise/2.11/v4/guides/intro-to-graphql/#discovering-the-graphql-api
# https://developer.github.com/v4/guides/forming-calls/#authenticating-with-graphql

from github import Github
from graphqlclient import GraphQLClient
import os
import json
import re


class LatestReleaseFetcher(object):
    """ Fetches the latest release given a client, an optional auth token, and
    a repository name """

    def __init__(self, client, repository_name="auto_pipeline"):
        self.client = client

        query = '''
        query {
          organization(login: "lims") {
            repository(name: "{repo_name}"){
              name,
              releases(last: 1) {
                edges {
                  cursor
                  node {
                    id
                    name
                    description
                  }
                }
              }
            }
          },
        }
        '''
        self.query = query.replace("{repo_name}", repository_name)

    def latest_release(self):
        # The release is assumed to have the pull requests for that release
        return self.client.execute(self.query)


class PRNumberParser(object):
    @classmethod
    def parse_pr_numbers(cls, release_text):
        # Parse out the description and get all of the pull requests with regex matching
        results_dict = json.loads(release_text)
        release_description = results_dict['data']['organization']['repository']['releases']['edges'][0]['node']['description']

        # match anything of the pattern "Merge pull request #..." and parse out any digits
        pr_lines = re.findall("#\d+", release_description)
        pr_nums = [re.findall("\d+", pr_line)[0] for pr_line in pr_lines]
        return pr_nums


class ReleasePRNumbersFetcher(object):
    """ Fetches a release and parses our pr numbers from the description."""

    DEFAULT_URL = 'https://github.counsyl.com/api/graphql'

    def __init__(self,
                 token,
                 url=DEFAULT_URL,
                 client=GraphQLClient,
                 repository_name='auto_pipeline',
                 release_fetcher=LatestReleaseFetcher,
                 pr_number_parser=PRNumberParser):

        self.client = client(url)
        self.client.inject_token(token)
        self.repository_name = repository_name
        self.release_fetcher = release_fetcher(
                        self.client,
                        repository_name=self.repository_name)
        self.pr_number_parser = pr_number_parser

    def pull_request_numbers(self):
        release = self.release_fetcher.latest_release()
        return self.pr_number_parser.parse_pr_numbers(release)


class BranchComparator(object):
    """ Compares a source and destination branch commits."""

    def __init__(self,
                 source,
                 destination,
                 client=Github,
                 repository_name='auto_pipeline'):

        self.client = client(token)
        self.source = source
        self.destination = destination
        self.repository_name = repository_name

        def pull_request_numbers(self):
            raise Exception("Not implemented")


class PRFetcher(object):
    """ Fetches pull request info from a pr number"""
    def __init__(self, client):
        self.client = client
        self.query = '''
        query {
            organization(login: "lims") {
                repository(name: "{repo_name}") {
                  name,
                  pullRequest(number: {pr_num}) {
                    title,
                    body,
                    number
                  }
                }
            }
        }
        '''

    def fetch_pr_descriptions(self, pr_nums, repository_name="auto_pipeline"):
        results = []
        for pr_num in pr_nums:
            query = self.query.replace("{pr_num}", pr_num)
            query = query.replace("{repo_name}", repository_name)

            results.append(json.loads(self.client.execute(query)))

        # Filter down to just the pr descriptions
        pr_descriptions = [result['data']['organization']['repository']['pullRequest'] for result in results]
        return pr_descriptions


class ReleaseNotesParser(object):
    def __init__(self, pr_descriptions):
        self.release_notes = []
        self.pr_descriptions = pr_descriptions

    def _parse_explicit_pr_information(self, pr_description):
        # Get key of form **CHANGE TYPE**: / **RISK**: / **RISK DESCRIPTION**: and parse
        # all text following until either \r\n is found OR <!-- then add each of those
        # to a dict where the key is the snake cased and downcased form of the same name.
        HEADINGS = ("CHANGE TYPE", "RISK", "RISK DESCRIPTION")
        HEADINGS_REGEX = "\*\*%s:*\*\*:*"
        END_REGEX = "(<!--|\r\n|\n)"

        body = pr_description['body']

        pr_notes = {}
        for heading in HEADINGS:
            try:
                start_payload_index = re.search(HEADINGS_REGEX % heading, body).end()
                body = body[start_payload_index:]
                end_payload_index = re.search(END_REGEX, body).start()
                pr_notes[heading] = body[:end_payload_index]
            except AttributeError:
                pr_notes[heading] = "NOT SET IN PR"
        return pr_notes

    def _search_for_ticket_name(self, notes, pr_description):
        PROJECTS = ("auto", "wetlab", "lims", "les", 'aci')
        TICKET_REG_EX = "%s(-| )\d+"

        # check_body for a JIRA link
        for project in PROJECTS:
            match = re.search(TICKET_REG_EX % project, pr_description['body'].lower())
            if match:
                return pr_description['body'][match.start():match.end()]

        # check title
        for project in PROJECTS:
            match = re.search(TICKET_REG_EX % project, notes['TITLE'].lower())
            if match:
                return notes['TITLE'][match.start():match.end()]

        return "NO TICKET IN PR"

    def parse_description(self, pr_description):
        END_DESCRIPTION = '## Release Notes'
        parts = pr_description['body'].split(END_DESCRIPTION)
        return parts[0]

    def parse_release_note(self, pr_description):
        notes = self._parse_explicit_pr_information(pr_description)
        notes['TITLE'] = pr_description['title'].upper()
        notes['PULL REQUEST'] = str(pr_description['number'])
        notes['JIRA TICKET'] = self._search_for_ticket_name(notes, pr_description)
        notes['DESCRIPTION'] = self.parse_description(pr_description)
        self.release_notes.append(notes)

    def parse_release_notes(self):
        for pr_description in self.pr_descriptions:
            self.parse_release_note(pr_description)
        return self.release_notes


class ReleaseNotesFormatter(object):
    """
    Consumes a dict or dicts likes so:
    {
      TITLE: "Some Title",
      DESCRIPTION: "Some description"
      TICKET: "LIMS-123",
      PULL_REQUEST: 123
      CHANGE_TYPE: "UI"
      RISK: "LOW",
      RISK_DESCRIPTION: "some description"
    }

    Output the parsed release notes as markdown:
    h2. SOME TITLE
    CHANGE_TYPE: UI
    DESCRIPTION: Some descriptions
    JIRA TICKET: LIMS-123
    PULL REQUEST: 123
    RISK: LOW
    RISK DESCRIPTION: Some description
    """
    @staticmethod
    def output(notes):
        PRINT_ORDER = [
            "TITLE",
            "DESCRIPTION",
            "CHANGE TYPE",
            "JIRA TICKET",
            "PULL REQUEST",
            "RISK",
            "RISK DESCRIPTION",
        ]

        for note in notes:
            for heading in PRINT_ORDER:
                content = note[heading]
                if heading == "TITLE":
                    print "h2. " + content
                else:
                    print heading + ": " + str(content)
            print
