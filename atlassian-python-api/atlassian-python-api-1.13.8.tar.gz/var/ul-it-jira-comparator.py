# coding:utf-8

from atlassian import Jira
from var import config
import logging
import pprint

ATLASSIAN_USER = "gonchik.tsymzhitov"
ATLASSIAN_PASSWORD = config.CONFLUENCE_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url="http://jira-uat.ullink.lan",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)


ATLASSIAN_USER = "gonchik.tsymzhitov"
ATLASSIAN_PASSWORD = config.CONFLUENCE_PASSWORD

logging.basicConfig(level=logging.ERROR)

it_jira = Jira(
    url="https://jira.orcsoftware.com",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

""" Status comparator """
statuses = jira.get_all_statuses()
ul_statuses = []
for status in statuses:
    ul_statuses.append(status['name'])

statuses = it_jira.get_all_statuses()

it_statuses = []
it_lower_statuses = []
for status in statuses:
    it_statuses.append(status['name'])
    it_lower_statuses.append(status['name'].lower())

for ul_status in ul_statuses:
    if ul_status not in it_statuses and ul_status.lower() in it_lower_statuses:
        print(ul_status)

""" Resolution comparator """
statuses = jira.get_all_resolutions()
ul_statuses = []
for status in statuses:
    ul_statuses.append(status['name'])

statuses = it_jira.get_all_resolutions()

it_statuses = []
it_lower_statuses = []
for status in statuses:
    it_statuses.append(status['name'])
    it_lower_statuses.append(status['name'].lower())

for ul_status in ul_statuses:
    if ul_status not in it_statuses and ul_status.lower() in it_lower_statuses:
        print(ul_status)
