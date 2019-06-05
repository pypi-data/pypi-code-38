from collections import defaultdict

class TrieNode():
    def __init__(self, isleaf=False):
        self.isLeaf = isleaf
        self.mapping = defaultdict(TrieNode)

    def get_mapping(self):
        return self.mapping

    def is_leaf(self):
        return self.isLeaf



