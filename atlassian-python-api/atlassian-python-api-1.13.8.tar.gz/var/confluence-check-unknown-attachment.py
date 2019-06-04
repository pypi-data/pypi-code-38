from atlassian import Confluence
from var import config
import logging

CONFLUENCE_URL = config.CONFLUENCE_URL
CONFLUENCE_LOGIN = config.CONFLUENCE_LOGIN
CONFLUENCE_PASSWORD = config.CONFLUENCE_PASSWORD

logging.basicConfig(level=logging.ERROR)


def check_unknown_attachment(conf, page_id):
    unknown_attachment_identifier = 'plugins/servlet/confluence/placeholder/unknown-attachment'
    result = conf.get_page_by_id(page_id, expand='body.view')
    body = result.get('body').get('view').get('value')
    if unknown_attachment_identifier in body:
        print(result.get('_links').get('base') + result.get('_links').get('tinyui'))


def get_all_pages_ids(conf, space_key):
    page_ids = []

    limit = 50
    flag = True
    step = 0
    while flag:
        values = conf.get_all_pages_from_space(space=space_key, start=step * limit, limit=limit)
        step += 1

        if len(values) == 0:
            flag = False
            print("Extracted all pages excluding restricts")
        else:
            for value in values:
                page_ids.append(value.get('id'))

    return page_ids


def check_unknown_attachment_in_space(confl, space_key):
    page_ids = get_all_pages_ids(confl, space_key)
    print("Start review pages {} in {}".format(len(page_ids), space_key))
    for page_id in page_ids:
        check_unknown_attachment(confl, page_id)


if __name__ == '__main__':
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_LOGIN,
        password=CONFLUENCE_PASSWORD,
        timeout=185
    )

    space_list = confluence.get_all_spaces()
    for space in space_list:
        if space['key'] == '~amber.voght':
            continue
        print("Start review {} space".format(space['key']))
        check_unknown_attachment_in_space(confluence, space['key'])
