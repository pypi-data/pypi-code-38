from bs4 import BeautifulSoup 
import requests
from urllib.parse import urljoin
import json


ENCODE_URL = "https://edu-search.nautide.com/"
DIC_SELECT_URL = "https://educalingo.com/en/dic-sel"


class EducalingoDictionary:
    def __init__(self):
        # set default language to english
        self.url = "https://educalingo.com/en/"
        self.lang = "en"
        self.search_url = urljoin(self.url, "dic-en")

        self.languages = None
        self.soup = None


    def __preprocess(self, word):
        params = {"dic": self.lang,
                  "q": word}
        page = requests.get(ENCODE_URL, params=params)
        # get the encoded word
        word = json.loads(page.content)['palabras']
        if word:
            return word[0]['url']


    def set_language(self, lang="en"):
        # set search language
        self.search_url = urljoin(self.url, f"dic-{lang}")
        self.lang = lang


    def search_word(self, word):
        # performs word search in educalingo
        word = self.__preprocess(word)
        if word is not None:
            url =  f"{self.search_url}/{word}"
            page = requests.get(url)
            self.soup = BeautifulSoup(page.text, 'lxml')


    def get_grammatical_category(self):
        # gets the grammatical class of the word
        if self.soup is not None:
            divs = self.soup.find("div", id="grammar")
            if divs is not None:
                for child in divs.find_all("div"):
                    child.decompose()
                return[div.get_text(strip=True) 
                       for div in divs.findAll("strong")][1:]


    def get_words_that_rhyme(self):
        # Gets the list of words that rhyme
        if self.soup is not None:
            divs = self.soup.findAll("div", class_="palabra_rima")
            rhyme_list = list()
            for div in divs:
                rhyme_list.append(div.get_text(strip=True))
            return rhyme_list


    def get_words_that_begin_like(self):
        if self.soup is not None:
            words_begin_div = self.soup.find("div", id="words-begin")
            divs = words_begin_div.findAll("div", class_="palabra_recuadro")
            words_begin = [div.get_text() for div in divs]
            return words_begin


    def get_words_that_end_like(self):
        if self.soup is not None:
            words_end_div = self.soup.find("div", id="words-end")
            divs = words_end_div.findAll("div", class_="palabra_recuadro")
            words_end = [div.get_text() for div in divs]
            return words_end


    def get_synonyms(self):
        # Gets the list of synonyms
        if self.soup is not None:
            divs = self.soup.find("div",
                                  class_="contenido_sinonimos_antonimos")
            if divs is not None:
                text = divs.get_text(strip=True)
                synonyms =  text.split("·")
                return synonyms


    def __get_text_from_div_translation(self, div):
        translation = div.span
        if translation is None:
            translation = div.find("a", text=True)
        return translation.get_text(strip=True)


    def get_translations(self):
        # Gets the list of available translations
        if self.soup is not None:
            divs = self.soup.findAll("div", class_="traduccion")
            translations = dict()
            for div in divs:
                language = div.strong.text
                translation = self.__get_text_from_div_translation(div)
                translations[div["id"]] = (language, translation)
            return translations


    def get_available_dictionaries(self):
        # list of available dictionaries in educalingo
        if self.languages is not None:
            return self.languages
        page = requests.get(DIC_SELECT_URL)
        soup = BeautifulSoup(page.text, 'lxml')
        languages = soup.findAll("div", class_="idioma_diccionario_seleccion")
        self.languages = dict()
        for dictionary in languages:
            dict_lang = dictionary.find("div",
                                        class_=
                                        ["idioma_diccionario_texto_seleccion",
                                        "idioma_diccionario_texto_seleccion_activo"])
            self.languages[dictionary.div.text] = dict_lang.get_text()
        return self.languages
