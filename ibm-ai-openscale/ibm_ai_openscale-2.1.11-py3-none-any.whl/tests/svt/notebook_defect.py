import requests

api_key = ""

iam_token = "Bearer eyJraWQiOiIyMDE5MDIwNCIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJJQk1pZC0zMTAwMDI3NTJHIiwiaWQiOiJJQk1pZC0zMTAwMDI3NTJHIiwicmVhbG1pZCI6IklCTWlkIiwiaWRlbnRpZmllciI6IjMxMDAwMjc1MkciLCJnaXZlbl9uYW1lIjoiTWFrc3ltaWxpYW4iLCJmYW1pbHlfbmFtZSI6IkVyYXptdXMiLCJuYW1lIjoiTWFrc3ltaWxpYW4gRXJhem11cyIsImVtYWlsIjoibWFrc3ltaWxpYW4uZXJhem11czFAcGwuaWJtLmNvbSIsInN1YiI6Ik1ha3N5bWlsaWFuLkVyYXptdXMxQHBsLmlibS5jb20iLCJhY2NvdW50Ijp7InZhbGlkIjp0cnVlLCJic3MiOiJlOWIwZWI0YTUxYjI0YWUzNTdhZGM5YTFiNDQ4MGUzMSIsImltc191c2VyX2lkIjoiNzI4MjYwMSIsImltcyI6IjE3MzM2NjcifSwiaWF0IjoxNTU5NjM0MTMyLCJleHAiOjE1NTk2Mzc3MzIsImlzcyI6Imh0dHBzOi8vaWFtLmNsb3VkLmlibS5jb20vaWRlbnRpdHkiLCJncmFudF90eXBlIjoidXJuOmlibTpwYXJhbXM6b2F1dGg6Z3JhbnQtdHlwZTpwYXNzY29kZSIsInNjb3BlIjoiaWJtIG9wZW5pZCIsImNsaWVudF9pZCI6ImJ4IiwiYWNyIjoxLCJhbXIiOlsicHdkIl19.EKfbCSTWkzb3wECWX8dOQ-TIxkg3VHITuvq9-a9eW0KFZg6AUvQ-pI9pNfGxCHBmOZ5mN8e3OzPMbIoG_4cKG0lU6r_-VvKS88SPPJQyyRhUrjUnSilpYZv1sTADi2oWh2y7jj8moU3Qqd2H8FWK1QokpxujyfkNoVwWnplE6yRYjDrzT2Ocnj3Yv3q9XiJoq3SCOomB8riiFKvJJw5mDZnUWWJbiF-4zVW5KadFhREV9bkSIzVaWMjZQSNaEYo1w_69frGNV2auBnfF2xwPDmlfUOVM8fWIxtoHXCgKsF7wvOalmMyipdH8fdWkMsKbNNE_IfxT5h4VnDV_zuqUvQ"

base_url = "https://api.dataplatform.cloud.ibm.com"

headers = {"Authorization": iam_token}

# response = requests.get("{}/v2/projects/d97e8bd4-e560-45c5-95c5-d9dae5acf1b1?include=everything".format(base_url), headers=headers)
# print(response.status_code)
# print(response.text)

# response = requests.get("{}/v2/projects/d97e8bd4-e560-45c5-95c5-d9dae5acf1b1/assets/f18346fb-98e0-4223-ad98-4ff7c9f7d2b0".format(base_url), headers=headers)
# print(response.status_code)
# print(response.text)
#

# response = requests.get("{}/v2/schedules?project_id={}".format(base_url, "d97e8bd4-e560-45c5-95c5-d9dae5acf1b1"), headers=headers)
# print(response.status_code)
# print(response.text)

notebook_url = "https://api.dataplatform.cloud.ibm.com/v2/notebooks"

response = requests.get("{}".format(notebook_url), headers=headers)
print(response.status_code)
print(response.text)

# schedule_url = "https://api.dataplatform.cloud.ibm.com/v2/schedules/865b0c0507129800d20c66543c0027b4?project_id=d97e8bd4-e560-45c5-95c5-d9dae5acf1b1"
# response = requests.get("{}".format(schedule_url), headers=headers)
# print(response.status_code)
# print(response.text)

# notebook_ex_id = "https://api.dataplatform.cloud.ibm.com/v2/notebook_executions"
# artifact_id = "a5e2ead4-b793-4d84-bbb7-f11a7761bae8"
#
# response = requests.get("{}".format(notebook_ex_id), headers=headers)
# print(response.status_code)
# print(response.text)


environments_url="https://api.dataplatform.cloud.ibm.com/v2/environments"