class TrieNode:

    def __init__(self):
        self._children = {}
        self._word = None

    def has_child(self, key):
        return key in self._children

    def get_child(self, key):
        return self._children[key]

    def insert_child(self, key):
        self._children[key] = TrieNode()

    @property
    def word(self):
        return self._word

    @word.setter
    def word(self, word):
        if not self._word:
            self._word = word
        else:
            raise AttributeError('Word can only be set once')


class Trie:

    def __init__(self):
        self.root = TrieNode()

    def __contains__(self, key):
        return self.exactly_search(key)

    def exactly_search(self, word: str):
        current = self.root
        for char in word:
            if not current.has_child(char):
                return False
            current = current.get_child(char)
        if current.word:
            return True
        return False

    def insert(self, word: str):
        current = self.root
        for char in word:
            if not current.has_child(char):
                current.insert_child(char)
            current = current.get_child(char)
        current.word = word

    def match_prefix(self, word: str, shortest: bool = False):
        current = self.root
        longest_word = None
        for char in word:
            if not current.has_child(char):
                return longest_word
            current = current.get_child(char)
            if current.word:
                longest_word = current.word
                if shortest:
                    return longest_word
        return longest_word
