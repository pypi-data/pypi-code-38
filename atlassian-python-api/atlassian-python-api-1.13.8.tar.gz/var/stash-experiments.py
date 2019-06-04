from atlassian import Stash
import config
import logging
import pprint

logging.basicConfig(level=logging.DEBUG)
stash = Stash(
    url=config.STASH_URL,
    username=config.CONFLUENCE_LOGIN,
    password=config.CONFLUENCE_PASSWORD
)

# (stash.get_tags('TB', 'tb', order_by="ALPHABETICAL", start=1400, limit=1400))
# print(stash.get_project_tags('TB', 'tb', '2.12.2.10*'))

pprint.pprint(stash.repo_list('TB'))
print(stash.get_mail_configuration())