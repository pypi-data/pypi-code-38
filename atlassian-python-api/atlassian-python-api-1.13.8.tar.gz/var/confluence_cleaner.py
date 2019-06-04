from atlassian import Confluence
import datetime
import config
import pprint
import logging

CONFLUENCE_URL = config.CONFLUENCE_URL
CONFLUENCE_LOGIN = config.CONFLUENCE_LOGIN
CONFLUENCE_PASSWORD = config.CONFLUENCE_PASSWORD
DRAFT_DAYS = 10

logging.basicConfig(level=logging.ERROR)


def clean_pages_from_space(space_key):
    """

    :param space_key:
    :return:
    """
    limit = 500
    flag = True
    step = 0
    while flag:
        values = confluence.get_all_pages_from_space_trash(space=space_key, start=0, limit=limit)
        step += 1
        if len(values) == 0:
            flag = False
            print("For this space trash is empty")
        else:
            for value in values:
                print(value['title'])
                confluence.remove_page_from_trash(value['id'])


def clean_all_trash_pages_from_all_spaces(confluence):
    limit = 50
    flag = True
    i = 0
    while flag:
        space_lists = confluence.get_all_spaces(start=i * limit, limit=limit)
        if space_lists and len(space_lists) != 0:
            i += 1
            for space_list in space_lists:
                print("Start review the space with key: " + space_list['key'])
                clean_pages_from_space(space_key=space_list['key'])
        else:
            flag = False


def clean_draft_pages_from_space(space_key, count, now):
    pages = confluence.get_all_draft_pages_from_space(space=space_key, start=0, limit=500)
    for page in pages:
        page_id = page['id']
        draft_page = confluence.get_draft_page_by_id(page_id=page_id)
        last_date_string = draft_page['version']['when']

        last_date = datetime.datetime.strptime(last_date_string.replace(".000", "")[:-6], "%Y-%m-%dT%H:%M:%S")
        if (now - last_date) > datetime.timedelta(days=DRAFT_DAYS):
            count += 1
            print("Removed page with date " + last_date_string)
    return count


def clean_all_draft_pages_from_all_spaces(confluence):
    now = datetime.datetime.now()
    count = 0
    limit = 50
    flag = True
    i = 0
    while flag:
        space_lists = confluence.get_all_spaces(start=i * limit, limit=limit)
        if space_lists and len(space_lists) != 0:
            i += 1
            for space_list in space_lists:
                print("Start review the space with key: " + space_list['key'])
                count = clean_draft_pages_from_space(space_key=space_list['key'], count=count, now=now)
        else:
            flag = False

    print("Script has been removed {count} draft pages older than {days} days".format(count=count, days=DRAFT_DAYS))


def page_version_remover(server, content_id, remained_page_numbers):
    response = server.get_content_history(content_id)
    if not response.get('latest'):
        return
    latest_version_count = int(response.get('lastUpdated').get('number'))
    if len(response) > 0 and latest_version_count > remained_page_numbers:
        # print("Number of latest version {}".format(latest_version_count))
        for version_page_counter in range(1, (latest_version_count - remained_page_numbers + 1), 1):
            server.remove_content_history(content_id, 1)
    else:
        # print('Number of page history smaller than remained')
        return


def get_all_page_ids_from_space(confluence, space_key):
    """
    :param confluence:
    :param space_key:
    :return:
    """
    limit = 500
    flag = True
    step = 0
    page_ids = []

    while flag:
        values = confluence.get_all_pages_from_space(space=space_key, start=limit * step, limit=limit)
        step += 1
        if len(values) == 0:
            flag = False
            print("Did not find any pages, please, check permissions in space {}".format(space_key))
        else:
            for value in values:
                print("Retrieve page in space {} with title: {}".format(space_key, value['title']))
                page_ids.append((value['id']))
    print("Found in space {} pages {}".format(space_key, len(page_ids)))
    return page_ids


def get_all_spaces(confluence):
    limit = 50
    flag = True
    i = 0
    space_key_list = []
    while flag:
        space_lists = confluence.get_all_spaces(start=i * limit, limit=limit)
        if space_lists and len(space_lists) != 0:
            i += 1
            for space_list in space_lists:
                print("Start review the space with key = " + space_list['key'])
                space_key_list.append(space_list['key'])
        else:
            flag = False

    return space_key_list


def reduce_page_numbers(confluence, page_id, remained_page_history_count):
    page_version_remover(confluence, page_id, remained_page_history_count)
    return


if __name__ == '__main__':
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_LOGIN,
        password=CONFLUENCE_PASSWORD
    )
    remained_count = 1
    space_keys = get_all_spaces(confluence)

    for space_key in space_keys:
        print("Starting review space {}".format(space_key))
        page_ids = get_all_page_ids_from_space(confluence, space_key)
        for page_id in page_ids:
            reduce_page_numbers(confluence, page_id=page_id, remained_page_history_count=remained_count)

    # clean_all_draft_pages_from_all_spaces(confluence=confluence)
    # clean_all_trash_pages_from_all_spaces(confluence=confluence)

    # confluence.clean_package_cache(cache_name='org.hibernate.cache.internal.StandardQueryCache_v5')
