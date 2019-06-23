#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import Modules
from bs4 import BeautifulSoup
import requests
import re


# List all available Countries
def list_countries():
    """List all available countries for extraction
    
    This function will create a connection to the
    website of the German Foreign Office and 
    fetch the latest list of available countries.
    

    Returns
    -----------
    The function returns None. However, a formatted
    list of countries is printed to the screen.
    Four countries per row, sperated by ' | '.
    """
    # Open First Page
    base_url = "https://www.auswaertiges-amt.de/de/ReiseUndSicherheit/reise-und-sicherheitshinweise"
    base_html = requests.get(base_url).content
    base_soup = BeautifulSoup(base_html, "lxml")
    
    # Collect Remaining Pages
    total_links = base_soup.find_all("a", {"class" : "pagination__list-link"})
    total_links = [base_url + "/" + x["href"] for x in total_links]
    total_links.append(base_url)
    
    # Function to list all Countries on Page with Link
    def _find_countries(url):
        # Find Content
        countries_html = requests.get(url).content
        countries_soup = BeautifulSoup(countries_html, "lxml")
        countries_boxes = countries_soup.find_all("div", 
                                                  {"class" : "c-teaser--country is-image-headline"})
        
        # Find Country Names
        countries_names = []
        for box in countries_boxes:
            headline = box.find("h3", {"class" : "teaser__headline"})
            country = headline.get_text().strip()
            countries_names.append(country)
            
        
        # Find Links
        countries_links = []
        for box in countries_boxes:
            link = box.find("a")["href"]
            link = "https://www.auswaertiges-amt.de"+link
            countries_links.append(link)
            
        # Join to Dict
        if len(countries_names) == len(countries_links):
            country_dict = dict(zip(countries_names, countries_links))
        else:
            raise ValueError("Number of Country Names and Number of Links does not match.")
            
        return(country_dict)
        
    # Collect all Countries on all Pages
    all_dict = dict()
    for link in total_links:
        dict_tmp = _find_countries(link)
        all_dict.update(dict_tmp)
        
    # Return all Countries in a Dictionary
    return(all_dict)
    
    
# Extract Information for a Single Country
def extract_country(url):
    """Scrape information for a given country
    
    Given a certain countries url, this function
    will return a dictionary containing
    information on country specific securitiy
    issues, general travel guidance, and medical
    issues. Every top category is subdivided
    by several sub-categories.
    
    The result will be a structured dictionary.
    
    Parameters
    -----------
    url: string
        The url of a single country as string.
        
    Returns
    -----------
    text_dict: A dictionary consisting of four
    top categories. Every top category is associated
    with another dictionary containing sub-categories
    for the respective top category.
    """
    # Find Raw Content
    country_html = requests.get(url).content
    country_soup = BeautifulSoup(country_html, "lxml")
    
    # Find Country Name
    country = country_soup.find("span", {"class" : "heading__title-text"}).get_text().strip()
    country = re.search("(^.+):", country).group(1)
    
    # Define Function to find Text for Section
    def _collect_text(start, end):
        siblings = start.next_siblings                      # Find Elements next to Header
        collect_dict = {}
        
        # Iterate through Siblings
        for sibling in siblings:
            if sibling.name == end:                         # Stop as soon as stop criterion is met
                break
            if sibling.name == "h3":
                sub_section = sibling.get_text().strip()
                sibling = next(siblings)
                while sibling == "\n":
                    sibling = next(siblings)
                text = sibling.get_text()
                text = re.sub("^"+sub_section, "", text)
                tmp_dict = {sub_section : text}
                collect_dict.update(tmp_dict)
            elif sibling.name == "p":                         # If Element is 'p', then add text
                try:
                    sub_section = sibling.em.get_text().strip()
                    text = sibling.get_text()
                    text = re.sub("^"+sub_section, "", text)
                    tmp_dict = {sub_section : text}
                    collect_dict.update(tmp_dict)
                except Exception:
                    pass
            
        # Define Result
        section_name = start.get_text()
        section_dict = {section_name : collect_dict}
        return(section_dict)
    
    # Init Dictionary to collect Information on Country
    text_dict = {"Country" : country}
    
   
    # Get Country Specific Info
    def _country_specific_filter(tag):
        cond1 = tag.name == "h2"
        cond2_1 = "Landesspezifische Sicherheitshinweise" in tag.get_text()
        cond2_2 = "Landesspezifischer Sicherheitshinweis" in tag.get_text()
        cond2_3 = "Sicherheit" in tag.get_text()
        return(cond1 & (cond2_1 | cond2_2 | cond2_3))
        
    start = country_soup.find(_country_specific_filter)
    end = "h2"
    specific_info = _collect_text(start, end)
    text_dict.update(specific_info)
    
    # Get General Information
    def _general_filter(tag):
        cond1 = tag.name == "h2"
        cond2_1 = "Allgemeine Reiseinformationen" in tag.get_text()
        cond2_2 = "Reiseinfos" in tag.get_text()
        return(cond1 & (cond2_1 | cond2_2))
        
    start = country_soup.find(_general_filter)
    end = "h2"
    general_info = _collect_text(start, end)
    text_dict.update(general_info)
    
    #Get Medical Information
    def _medical_filter(tag):
        cond1 = tag.name == "h2"
        cond2_1 = "Medizinische Hinweise" in tag.get_text()
        cond2_2 = "Gesundheit" in tag.get_text()
        return(cond1 & (cond2_1 | cond2_2))
        
    start = country_soup.find(_medical_filter)
    end = "h2"
    medical_info = _collect_text(start, end)
    text_dict.update(medical_info)
    
    return(text_dict)