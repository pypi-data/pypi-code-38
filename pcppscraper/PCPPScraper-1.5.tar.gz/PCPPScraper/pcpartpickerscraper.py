from requests import get
from bs4 import BeautifulSoup

class Component():
    def __init__(self, componentType, name, link, price):
        self.type = componentType
        self.name = name
        self.link = link
        self.price = price

def getComponents(URL : str):
    page = get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    components = soup.find_all(attrs = {'class' : 'tr__product'})
    componentList = list()
    for component in components:
        componentLink = component.find(attrs = {'class' : 'td__name'}).find('a')
        if componentLink == None:
            break
        componentType = component.find(attrs = {'class' : 'td__component'}).find('a').get_text()
        price = component.find(attrs = {'class' : 'td__price'}).find('a')
        if price == None:
            price = 'unknown'
            if component.find(attrs = {'class' : 'td__price'}).get_text() != None:
                price = component.find(attrs = {'class' : 'td__price'}).get_text()[5:]
        else:
            price = price.get_text()
        name = componentLink.get_text()
        link = 'https://pcpartpicker.com' + componentLink.get('href')
        newComponent = Component(componentType, name, link, price)
        componentList.append(newComponent)
        

    return componentList

def searchComponents(resultCount, query):
    query = query.replace('+', '%2B')
    URL = 'https://pcpartpicker.com/search/?q=' + query
    page = get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    components = soup.find_all(attrs = {'class' : 'search_results--contentWrapper'})
    componentList = list()
    if components == None:
        return componentList
    i = 0
    
    for component in components:
        nameAndLink = component.find(attrs = {'class' : 'search_results--link'})
        name = nameAndLink.find('a').get_text()
        link = 'https://pcpartpicker.com' + nameAndLink.find('a').get('href')
        price = component.find(attrs = {'class' : 'search_results--price'}).find('a').get_text()
        if price == None:
            price = 'unknown'
        componentPage = get(link)
        typeSoup = BeautifulSoup(componentPage.content, 'html.parser')
        componentType = typeSoup.find(attrs= {'class' : 'pageTitle--categoryTitle'}).find('a').get_text()
        
        newComponent = Component(componentType, name, link, price)
        componentList.append(newComponent)
        i+=1
        if i >= resultCount:
            break

    return componentList