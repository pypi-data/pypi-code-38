from trienode import TrieNode

class trie:
    def __init__(self, head=None):
        self.root = None
        self.trie_size = 0

    def insert(self, value):
        curr = self.root

        if self.root == None:
            self.root = TrieNode()
            curr = self.root

        for token in value:
            if token in curr.get_mapping():
                curr = curr.get_mapping()[token]
            else:
                curr.get_mapping()[token] = TrieNode()
                curr = curr.get_mapping()[token]

        curr.isLeaf = True
        self.trie_size = self.trie_size + 1

    def search(self, value):
        if self.root == None:
            return False

        curr = self.root

        for token in value:

            if token not in curr.get_mapping():
                return False
            else:
                curr = curr.get_mapping()[token]

        return curr.isLeaf

    def __dfs(self, start_char, next_link, helper, sugg):
        helper = helper + start_char

        if next_link.is_leaf():
            sugg.append(helper)

        for k, v in next_link.get_mapping().items():
            self.__dfs(k, v, helper, sugg)

    def suggestions(self, prefix):
        sugg = []

        if self.root == None:
            return sugg

        curr = self.root

        for token in prefix:
            if token not in curr.get_mapping():
                return sugg
            else:
                curr = curr.get_mapping()[token]

        helper = ''
        for key, val in curr.get_mapping().items():
            self.__dfs(key, val, helper, sugg)

        for i in range(len(sugg)):
            sugg[i] = prefix + sugg[i]

        return sugg

    def size(self):
        return self.trie_size