# coding:utf-8

from atlassian import Jira
from var import config
import logging
import pprint
import subprocess
import time

ATLASSIAN_USER = "gonchik.tsymzhitov"
ATLASSIAN_PASSWORD = config.CONFLUENCE_PASSWORD

logging.basicConfig(level=logging.ERROR)

jira = Jira(
    url="https://jira.orcsoftware.com",
    username=ATLASSIAN_USER,
    password=ATLASSIAN_PASSWORD)

db_result = open('db_result', 'r')
i = 0
cookie = """-H 'cookie: AJS.conglomerate.cookie="|"; amplitude_id_472c19f49ee467477d12639c21dac922orcsoftware.com=eyJkZXZpY2VJZCI6ImFiZTIzNDhjLTQ3YTItNDY2ZS04OTQzLTlmN2M5MTUxYzUyMFIiLCJ1c2VySWQiOiJTRU4tOTc4MDg1MiAtIEl0aXZpdGkgR3JvdXAgQUIiLCJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOjE1MzM4MDQ1OTc4MzcsImxhc3RFdmVudFRpbWUiOjE1MzM4MDQ2Mzg0NTEsImV2ZW50SWQiOjEwLCJpZGVudGlmeUlkIjowLCJzZXF1ZW5jZU51bWJlciI6MTB9; jira.editor.user.mode=source; atlassian.xsrf.token=ANH0-SK2H-WTTE-HFNJ_caa198e29b8c8bd7f78639fe3d4d5b9fd6597eca_lin; JSESSIONID=ED94F1375083DD5572A2FFA2D84AA56A'"""
print("PKEY \t DB \t LUCENE")
project_key = 'CATS'
command = """ curl  --silent 'https://jira.orcsoftware.com/secure/admin/IndexProject.jspa'  -H 'content-type: application/x-www-form-urlencoded' {} --data 'confirmed=true&key={}' --compressed""".format(cookie,
    project_key)
print(subprocess.call(command, shell=True))
for line in db_result:
    i += 1
    if i < 45:
        continue
    # if i > 160:
    #    break
    total_db_issues, project_key = line.split(',')
    total_db_issues = total_db_issues.replace("'", '').strip()
    project_key = project_key.replace("'", '').strip()
    print("Start review {}".format(project_key))
    jql_query = 'project = "{}"'.format(project_key)
    total_issues = jira.jql(jql_query).get('total')
    if total_issues is None:
        continue
    if int(total_issues) < int(total_db_issues):
        print("{} \t {} \t {}".format(project_key, total_db_issues, total_issues))
        command = """ curl  --silent 'https://jira.orcsoftware.com/secure/admin/IndexProject.jspa'  -H 'content-type: application/x-www-form-urlencoded' {} --data 'confirmed=true&key={}' --compressed""".format(
            cookie, project_key)
        result = subprocess.call(command, shell=True)
        if result == 0:
            time.sleep(20)
        else:
            time.sleep(1)


"""
curl -u login:pass -X POST --data @body.json -H "Content-type: application/json"
<jira_url>/rest/scriptrunner/latest/canned/com.onresolve.scriptrunner.canned.jira.admin.ReindexIssues

"""
