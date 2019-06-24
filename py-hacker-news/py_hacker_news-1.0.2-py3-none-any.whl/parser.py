from bs4 import BeautifulSoup


def createResultArray(responseText):
    # This function takes a single hackernews page's html content and parses
    # it using BeautifulSoup and returns a list of dictionaries containg
    # title, url, points, age.
    soup = BeautifulSoup(responseText, "html.parser")
    titles = soup.findAll("a", class_="storylink")
    points = soup.findAll("span", class_="score")
    ages = soup.findAll("span", class_="age")
    results_array = []
    for title, point, age in zip(titles, points, ages):
        temp = {}
        temp["name"] = title.text
        temp["url"] = title["href"]
        temp["points"] = point.text
        temp["age"] = age.text
        results_array.append(temp)
    return results_array
