from threading import Thread
from atlassian import Confluence
import datetime
import config
import pprint
import logging
from var import confluence_cleaner

CONFLUENCE_URL = config.CONFLUENCE_URL
CONFLUENCE_LOGIN = config.CONFLUENCE_LOGIN
CONFLUENCE_PASSWORD = config.CONFLUENCE_PASSWORD
DRAFT_DAYS = 10

logging.basicConfig(level=logging.ERROR)


class CleanerThread(Thread):

    def __init__(self, space_key, remained_count_page, name):
        Thread.__init__(self)
        self.name = name
        self.space_key = space_key
        self.remained_count = remained_count_page

    def run(self):
        print("Starting review space with key {}".format(self.space_key))
        page_ids = confluence_cleaner.get_all_page_ids_from_space(confluence, self.space_key)
        for page_id in page_ids:
            confluence_cleaner.reduce_page_numbers(confluence, page_id=page_id,
                                                   remained_page_history_count=self.remained_count)
        msg = "{} finished work with {} !".format(self.name, self.space_key)
        print(msg)


def main(jobs, remained_count_page):
    """
    Run the program
    """
    for item, space_key in enumerate(jobs):
        name = "Thread %s" % (item + 1)
        thread = CleanerThread(space_key, remained_count_page, name)
        thread.start()


if __name__ == '__main__':
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_LOGIN,
        password=CONFLUENCE_PASSWORD
    )
    remained_count = 1
    space_keys = confluence_cleaner.get_all_spaces(confluence)
    main(space_keys, remained_count)