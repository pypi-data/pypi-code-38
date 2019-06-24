import requests
from .parser import createResultArray

baseURL = "https://news.ycombinator.com/"

# all the functions below take number of pages as optional parameter.
# Default value is 1 ie., a single page is fetched. Valid range is 1 - 5
# The first page is fetched regardless of the argument passed


def getNews(pages, proxy):
    # This is the default request made if no args are passed at runtime.
    # This function fetches the news shown on the hackernews homepage
    resultsArray = []
    resultsArray = resultsArray + createResultArray(getSinglePage(baseURL + "news", proxy=proxy))
    if pages == 1:
        # If the user requested only a single page, return these results
        return resultsArray
    for page in range(2, pages):
        resultsArray = resultsArray + createResultArray(
            getSinglePage(baseURL + "news", params={"p": page}, proxy=proxy)
        )
    return resultsArray


def getLatest(pages, proxy):
    # This function is called when the user passes 'latest' arg
    # Fetches the the newest articles from the site
    resultsArray = []
    resultsArray = resultsArray + createResultArray(getSinglePage(baseURL + "newest", proxy=proxy))
    if pages == 1:
        # If the user requested only a single page, return these results
        return resultsArray
    for page in range(2, pages):
        resultsArray = resultsArray + createResultArray(
            getSinglePage(baseURL + "newest", {"p": page}, proxy)
        )
    return resultsArray


def getPast(formattedDate, pages, proxy):
    # This function is called if the user passes 'past' arg
    # The user can pass a specific date of number of dates in the past argument
    resultsArray = []
    resultsArray = resultsArray + createResultArray(
        getSinglePage(baseURL + "front", {"day": formattedDate},proxy)
    )
    if pages == 1:
        # If the user requested a single page from the date
        return resultsArray
    for page in range(2, pages):
        resultsArray = resultsArray + createResultArray(
            getSinglePage(baseURL + "front", {"p": page, "day": formattedDate}, proxy)
        )
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
