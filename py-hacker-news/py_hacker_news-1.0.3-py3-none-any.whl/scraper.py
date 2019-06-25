import requests
from .parser import createResultArray

baseURL = "https://news.ycombinator.com/"

# all the functions below take number of pages as optional parameter.
# Default value is 1 ie., a single page is fetched. Valid range is 1 - 5
# The first page is fetched regardless of the argument passed

def getArticles(pages, proxy, newsType, formattedDate=None):
    # This function fetches required number of pages of the required type from the site
    # Previously there used to be a function for each type of news, but I have decided to 
    # merge them into one to avoid redundancy and Keep It Simple
    resultsArray = []
    url = baseURL + newsType    # newsType can be on of news, newest or front (for past news)
    params = {} if formattedDate == None else {"day" : formattedDate}
    resultsArray = resultsArray + createResultArray(getSinglePage(url, proxy=proxy, params=params))
    if pages == 1:
        return resultsArray;
    for page in range(2, pages):
        # add a page parameter to params dict 
        params["p" : page]
        resultsArray = resultsArray + createResultArray(getSinglePage(url, params=params, proxy=proxy))
    return resultsArray

# Utility Functions
def getSinglePage(url=baseURL, params={}, proxy=None):
    # This function obtains a single page from the hackernews website
    # It takes a url and parameters to pass
    # This function takes of error handling too
    try:
        response = requests.get(url, params, proxies={"https":proxy, "http":proxy}, timeout = 15)
        if response.status_code != 200:
            # If the request failed show error and exit()
            printConnectionError()
            exit()
        return response.text
    except Exception:
        printConnectionError()
        exit()


def printConnectionError():
    print(
        "Unable to fetch data from hacker news."
        + " Please check your internet connection and try again...\n"
        + "If the issue persists please open an issue on github\n"
        + "https://github.com/saivarshith2000/hacker_news_cli/issues"
    )
    return
