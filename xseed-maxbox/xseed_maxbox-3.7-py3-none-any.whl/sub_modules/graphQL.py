import requests

headers = {
  "Authorization": "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmhjSEJKYm1adklqcDdJbTVoYldVaU9pSmhjSEJ2Ym1VaWZTd2lhV0YwSWpveE5URXdPRGs0T1RBemZRLldPcGV3TzBOUmVxVG9ORWw0UGlma3I4akdQYWhPbzcwTDh3aVY0cVJHTUE6Og=="
}
minicampusCode = "mhnqct"

# A simple function to use requests.post to make the API call.Note the json = section.
def run_query(query):
  request = requests.post('http://api.xseedstaging.com/graphql/core', json = {
    'query': query
  }, headers = headers)
  if request.status_code == 200:
    return request.json()
  else :
    raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

# The GraphQL query(with a few aditional bits included) itself defined as a multi - line string.
query = """
{
miniCampus(code: {minicampusCode})
{
id
grades }
}"""

result = run_query(query)# Execute the query
print(result)
