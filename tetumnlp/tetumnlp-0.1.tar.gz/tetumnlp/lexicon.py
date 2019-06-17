import os
import time
import string
import csv
import re
import unicodedata

class Lexicon:

    def __init__(self):

        self.pathToWordlist = "wordlist"
        self.build()

    def build(self):

        self.dictionary = []
        filename = os.path.join(os.path.dirname(__file__), self.pathToWordlist)

        with open(filename, 'r') as csvfile:
            rd = csv.reader(csvfile, delimiter='\t', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            next(rd) #skip header
            for r in rd:
                if r[0].strip():
                    self.dictionary.append({
                        'english': r[0].strip(),
                        'tetum': r[1].strip(),
                        'from': r[2].strip(),
                        'category': r[3].strip(),
                        'frequency': r[4].strip(),
                        'pos': r[5].strip(),
                        'alternatives': r[6].strip(),
                        'posSentiment': float(r[7].strip()) if r[7].strip() else 0,
                        'negSentiment': float(r[8].strip()) if r[8].strip() else 0,
                        'words': [s.strip(string.punctuation) for s in r[1].split()]                    })
                    
                    if r[6].strip():
                        alternatives = r[6].split(',')
                        for a in alternatives:
                            if a.strip():
                                self.dictionary.append({
                                    'english': r[0].strip(),
                                    'tetum': a.strip(),
                                    'from': r[2].strip(),
                                    'category': r[3].strip(),
                                    'frequency': r[4].strip(),
                                    'pos': r[5].strip(),
                                    'alternatives': r[6].strip(),
                                    'posSentiment': float(r[7].strip()) if r[7].strip() else 0,
                                    'negSentiment': float(r[8].strip()) if r[8].strip() else 0,
                                    'words': [s.strip(string.punctuation) for s in r[1].split()]
                                })
                                
                    decode = self.strip_accents(r[1])
                    if decode != r[1]:
                        self.dictionary.append({
                            'english': r[0].strip(),
                            'tetum': decode.strip(),
                            'from': r[2].strip(),
                            'category': r[3].strip(),
                            'frequency': r[4].strip(),
                            'pos': r[5].strip(),
                            'alternatives': r[6].strip(),
                            'posSentiment': float(r[7].strip()) if r[7].strip() else 0,
                            'negSentiment': float(r[8].strip()) if r[8].strip() else 0,
                            'words': [s.strip(string.punctuation) for s in decode.split()]
                        })	
                            
        for i in self.dictionary:
            i['tetum'] = re.sub(r'\([^)]*\)', '', i['tetum']).strip()
        

    def strip_accents(self, s):
        """
        Sanitarize the given unicode string and remove all special/localized
        characters from it.
    
        Category "Mn" stands for Nonspacing_Mark
        """
        try:
            return ''.join(
                c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn'
            )
        except:
            return s


    def get_first_definition(self, definitions):
        
        remove = re.sub(r'\([^)]*\)', '', definitions).strip()
        
        first = re.split('; |, ', remove)[0].replace('.','').replace(';','').strip()

        return first

    def get_definitions(self, definitions):

        remove_brackets = re.sub(r'\([^)]*\)', '', definitions).strip()

        return [i.strip(string.punctuation).strip() for i in re.split('; |, ', remove_brackets)]   
        
 
    def strip_punctuation(self, text):

        return text.translate(None, string.punctuation)
