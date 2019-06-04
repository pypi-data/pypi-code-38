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

    def __init__(self, page_id, remained_count, name):
        Thread.__init__(self)
        self.name = name
        self.page_id = page_id
        self.remained_count = remained_count

    def run(self):
        confluence_cleaner.reduce_page_numbers(confluence, page_id=self.page_id,
                                               remained_page_history_count=self.remained_count)
        msg = "%s finished work with %s!" % (self.name, self.page_id)
        print(msg)


def main(page_ids, remained_count):
    """
    Run the program
    """
    for item, page_id in enumerate(page_ids):
        name = "Thread %s" % (item + 1)
        thread = CleanerThread(page_id, remained_count, name)
        thread.start()


if __name__ == '__main__':
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_LOGIN,
        password=CONFLUENCE_PASSWORD
    )
    remained_count = 1
    space_keys = confluence_cleaner.get_all_spaces(confluence)

    for space_key in space_keys:
        print("Starting review space with key {}".format(space_key))
        page_ids = confluence_cleaner.get_all_page_ids_from_space(confluence, space_key)
        main(page_ids, remained_count)
        # for page_id in page_ids:
        #    confluence_cleaner.reduce_page_numbers(confluence, page_id=page_id, remained_page_history_count=remained_count)
