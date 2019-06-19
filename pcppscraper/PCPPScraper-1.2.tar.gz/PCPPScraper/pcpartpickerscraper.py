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
        else:
            price = price.get_text()
        name = componentLink.get_text()
        link = 'https://pcpartpicker.com' + componentLink.get('href')
        newComponent = Component(componentType, name, link, price)
        componentList.append(newComponent)
        

    return componentList

