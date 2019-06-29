import re
from .base import (
    ANNOTATIONS_REGEX,
    WikipediaScraperBase,
)
from ..filters.film import WikipediaFilmFilter


class WikipediaFilmScraper(WikipediaScraperBase):

    filter_class = WikipediaFilmFilter
    disambiguation_id = "Film_and_television"
    disambiguation_keyword = "film"

    def make_data(self, url, soup):
        data = super().make_data(url, soup)
        data["plot"] = self.filter_plot(soup)
        data.update(self.filter_genre_and_year(data["description"]))
        return data

    def filter_genre_and_year(self, description):
        year = ""
        genre = ""
        try:
            first_sentence = description.split(".")[0]
            try:
                pattern = r"^.+(\d{4})(.+)film.+$"
                found = re.search(pattern, first_sentence)
                year = found.group(1).strip()
                genre = found.group(2).strip().lower()
            except AttributeError:
                pass
        except IndexError:
            pass
        # Try to convert the year to an integer.
        try:
            year = int(year)
        except ValueError:
            pass
        return {
            "year": year,
            "genre": genre,
        }

    def filter_plot(self, soup):
        try:
            # Collect the text data from the paragraph elements.
            paragraphs = []
            # Find the plot element on the page.
            el = soup.findAll(id="Plot")[0]
            # Find its parent, since its in an H2 container.
            parent = el.parent
            if parent.name == "h2":
                # Then get the paragraphs that follow it.
                sib = parent.findNextSibling()
                while sib.name == "p":
                    paragraph = sib.getText().strip()
                    # remove footnote annotations
                    paragraph = re.sub(
                        ANNOTATIONS_REGEX,
                        "",
                        paragraph
                    )
                    paragraphs.append(paragraph)
                    # get the next sibling to check if its another paragraph.
                    sib = sib.findNextSibling()
            # Combine the paragraphs text together to form the plot.
            plot = " ".join(paragraphs)
            return plot
        except IndexError:
            return ""
