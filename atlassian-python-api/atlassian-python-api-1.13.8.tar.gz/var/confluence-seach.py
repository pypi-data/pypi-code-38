from atlassian import Confluence
import config
import pprint
import logging

CONFLUENCE_URL = config.CONFLUENCE_URL
CONFLUENCE_LOGIN = config.CONFLUENCE_LOGIN
CONFLUENCE_PASSWORD = config.CONFLUENCE_PASSWORD

logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_LOGIN,
        password='blablabla'
    )
    pprint.pprint(confluence.cql('text ~ gonchik'))