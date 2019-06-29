import re
from find_best_string import find_best_string

from ..utils import int_to_roman


class WikipediaFilterBase(object):
    def description_has_keywords(self, description):
        if any(x in description for x in self.keywords):
            return True
        return False

    def description_has_name(self, description, name):
        # If name is in the description, then return true
        if name in description:
            return True
        # Otherwise, find the best matching string.
        match, value = find_best_string(name, description)
        # If it matches 0.94 or higher, try to check the characters.
        if value >= 0.94:
            # Find the characters that are different.
            diff = tuple(set(name).symmetric_difference(set(match)))
            # Save whetehre each different character is alphanumeric or not
            # ie: A-Z or ':' or '_'
            alphanumeric = []
            for char in diff:
                if char.isalpha() or char.isnumeric():
                    alphanumeric.append((char, True))
                else:
                    alphanumeric.append((char, False))
            # If it only contains extra non-alphanumeric characters,
            # then consider it a match, and return true.
            if all(t[1] is False for t in alphanumeric):
                return True
        # Otherwise, return false.
        return False

    def url_has_name(self, url, name):
        name_lower = name.lower()
        name_lower_underscore = name_lower.replace(" ", "_")
        name_lower_slug = name_lower.replace(" ", "-")
        return any(
            x in url.lower()
            for x in [name_lower, name_lower_underscore, name_lower_slug]
        )

    def clean_description(self, description):
        description = description.lower()
        description = re.sub(r"[^\x00-\x7F]", " ", description)
        description = re.sub(r"\n", " ", description)
        description = re.sub("'", "", description)
        description = re.sub("'", "", description)
        description = re.sub(r"\s\s+", " ", description)
        return description

    # add conditional for names that already include keyword in the official
    # title. ie: "A serbian film", etc.
    def clean_name(self, name):
        name = name.lower()
        name = re.sub(r"({})$".format("|".join(self.keywords)), "", name)
        name = name.strip()
        return name

    def filter(self, name, scraped_data):
        result = None
        name = self.clean_name(name)
        while len(scraped_data) != 0:
            item = scraped_data.pop(0)
            if result is None:
                url = item["url"]
                raw_description = item["description"]
                if raw_description is None:
                    continue
                cleaned_description = self.clean_description(raw_description)
                if len(cleaned_description) == 0:
                    continue
                if self.description_has_name(cleaned_description, name):
                    if self.description_has_keywords(cleaned_description):
                        result = item
                else:
                    try:
                        m = re.search(r"\d+", name)
                        number = m.group(0)
                        roman = int_to_roman(int(number))
                        roman_name = name.replace(number, roman)
                        roman_name_lower = name.replace(number, roman.lower())
                        if self.decription_has_name(cleaned_description, roman_name):
                            if self.description_has_keywords(cleaned_description):
                                result = item
                        if self.decription_has_name(
                            cleaned_description, roman_name_lower
                        ):
                            if self.description_has_keywords(cleaned_description):
                                result = item
                        if self.url_has_name(url, roman_name):
                            result = item
                        if self.url_has_name(url, roman_name_lower):
                            result = item
                    except AttributeError:
                        pass
                if self.url_has_name(url, name):
                    result = item
        return result
