# coding: utf8
from atlassian import Confluence
import config
confluence = Confluence(
    url="https://itivitinet.itiviti.com",
    username=config.ATLASSIAN_LOGIN,
    password=config.ATLASSIAN_PASSWORD)



# If you know page_id of the page
content2 = confluence.get_page_by_id("97223980")

print(content2)
