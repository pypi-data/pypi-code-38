import requests
from bs4 import BeautifulSoup as bs
from enum import Enum
from urllib.parse import urlparse
from os.path import basename
import re


class BestSellerBookType(Enum):

    fiction = 'https://www.steimatzky.co.il/carousel/index/index/id/1080/'
    childrens = 'https://www.steimatzky.co.il/carousel/index/index/id/1084/'
    non_fiction = 'https://www.steimatzky.co.il/carousel/index/index/id/1086/'
    other = 'https://www.steimatzky.co.il/carousel/index/index/id/1088/'


class BookTypes(Enum):

    new = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D/%D7%97%D7%93%D7%A9%D7%99%D7%9D.html'
    english_all = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D-%D7%91%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%AA.html'
    english_fiction = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D-%D7%91%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%AA/fiction.html'
    english_children = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D-%D7%91%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%AA/children.html'
    english_nonfiction = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D-%D7%91%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%AA/non-fiction.html'
    english_israel_and_jewish_interest = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D-%D7%91%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%AA/israel-jewish-interest.html'
    english_art_design = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D-%D7%91%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%AA/art-design.html'
    english_map_and_guides = 'https://www.steimatzky.co.il/%D7%A1%D7%A4%D7%A8%D7%99%D7%9D-%D7%91%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%AA/maps-guides.html'
    games_box_games = 'https://www.steimatzky.co.il/%D7%9E%D7%A9%D7%97%D7%A7%D7%99%D7%9D/%D7%9E%D7%A9%D7%97%D7%A7%D7%99-%D7%A7%D7%95%D7%A4%D7%A1%D7%90.html'
    games_puzzles = 'https://www.steimatzky.co.il/%D7%9E%D7%A9%D7%97%D7%A7%D7%99%D7%9D/%D7%A4%D7%90%D7%96%D7%9C%D7%99%D7%9D.html'
    gifts_office_equipment = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%A6%D7%99%D7%95%D7%93-%D7%9E%D7%A9%D7%A8%D7%93%D7%99.html',
    gifts_digital_products = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%9E%D7%95%D7%A6%D7%A8%D7%99%D7%9D-%D7%93%D7%99%D7%92%D7%99%D7%98%D7%9C%D7%99%D7%99%D7%9D.html'
    gifts_souvenirs = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%9E%D7%96%D7%9B%D7%A8%D7%95%D7%AA.html'
    gifts_paper_products = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%99%D7%95%D7%9E%D7%A0%D7%99%D7%9D-%D7%90%D7%9C%D7%91%D7%95%D7%9E%D7%99%D7%9D-%D7%95%D7%9E%D7%95%D7%A6%D7%A8%D7%99-%D7%A0%D7%99%D7%99%D7%A8.html'
    gifts_toys = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%A6%D7%A2%D7%A6%D7%95%D7%A2%D7%99%D7%9D.html'
    gifts_jewellery = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%AA%D7%9B%D7%A9%D7%99%D7%98%D7%99%D7%9D.html'
    gifts_hobbies = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%9E%D7%95%D7%A6%D7%A8%D7%99-%D7%A4%D7%A0%D7%90%D7%99.html'
    gifts_mental_health = 'https://www.steimatzky.co.il/%D7%9E%D7%AA%D7%A0%D7%95%D7%AA-%D7%95%D7%A4%D7%A0%D7%90%D7%99/%D7%9E%D7%95%D7%93%D7%A2%D7%95%D7%AA-%D7%92%D7%95%D7%A3-%D7%95%D7%A0%D7%A4%D7%A9.html'


class Item:

    def __init__(self, title, author, url, image):
        self.title = title
        self.author = author
        self.url = url
        self.image = image
        #self.price = price
        #self.price_for_loyalty_customers = price_for_loyalty_customers


class Author:

    def __init__(self, name, url):
        self.name = re.sub(r'[\s+]', '', name)
        self.url = url

    def get_books(self):
        SteimatzkyScraper.__add_items(self.url)


class SteimatzkyScraper:

    def __init__(self):
        self.requests_session = requests.Session()

    def search_for_items(self, q):
        return SteimatzkyScraper.__add_items('https://www.steimatzky.co.il/catalogsearch/result/', params={'q': q})

    def get_bestsellers_by_genre(self, best_seller_book_type=BestSellerBookType.fiction):
        return SteimatzkyScraper.__add_items(best_seller_book_type.value)

    def find_books_by_type(self, book_type=BookTypes.new):
        return SteimatzkyScraper.__add_items(book_type.value)

    @staticmethod
    def __get_id_from_url(url):
        return int(basename(urlparse(url).path))

    @staticmethod
    def __add_items(url, params={}):
        html = requests.get(url, params=params).content.decode()
        soup = bs(html, 'html.parser')
        book_tags = soup.find_all('div', {'class': 'inner'})
        books = []
        for book_tag in book_tags:
            books.append(SteimatzkyScraper.__add_item(book_tag))
        return books

    @staticmethod
    def __add_item(book_tag):
        product_hover = book_tag.find('div', {'class': 'product-hover'})
        book_details = book_tag.find('div', {'class': 'details'})
        h4 = book_details.find('h4', {'class': 'bookTitle'})
        book_title = h4.find('a').string
        book_url = h4.find('a').get('href')
        book_author_span = book_details.find('span', {'class': 'bookAuthor'})

        book_author = Author(
            name=book_author_span.find('a').string,
            url=book_author_span.find('a').get('href')
        )

        #price_box = product_hover.find('div', {'class': 'price-box'})
        #price_box_loyalty = product_hover.find('div', {'class': 'price-box  sale'})

        return Item(
            title=book_title,
            author=book_author,
            url=book_url,
            image=product_hover.find('a', {'class': 'product-image'}).find('span').find('img').get('src')
            #price=self.__get_price(price_box),
            #price_for_loyalty_customers=self.__get_price(price_box_loyalty)
        )
