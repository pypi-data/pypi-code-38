#
# Hydra
# A nested dictionary to form a trie
# It holds a last key '_' when a word terminates, and the value of that is a set.
# The set holds any values we want by inserting elements one at a time
# via the insert_word function
#

class Hydra:
    def __init__(self, lst_words):
        self.head_d = {}

    def insert_word(self, word, code):
        """Insert a word (string) and add code (value) to termination set"""
        tmpd = self.head_d 
        for letter in word.strip():
            if not tmpd.get(letter, None):
                tmpd[letter] = {}
            tmpd = tmpd[letter]

        if tmpd.get('_', None):
            tmpd['_'].add(code)
        else:
            tmpd['_'] = {code}
        return tmpd
            
    def lookup(self, word):
        """Retrieve the set with terminators for a given word"""
        try:
            return eval("self.head_d['"+"']['".join(list(word))+"']['_']")
        except:
            return None
    
    def get_level(self, word):
        """Retrieve dict or endpoing of given word"""
        try:
            return eval("self.head_d['"+"']['".join(list(word))+"']")
        except:
            return None            
