"""
Module contain Node entity used in binary tree
which are applied in compression algorithms
"""


class Node:
    """Class representing a Node data structure in the binary tree"""
    def __init__(self, char, frequency, left=None, right=None):
        self.char = char
        self.frequency = frequency
        self.left = left
        self.right = right

    def __str__(self):
        return "({}: {})".format(self.char, self.frequency)

    def __lt__(self, other):
        """
            Help decide about order of inserting to Priority Queue
            based on frequency of occurrences:
                return True if other is greater
        """
        return self.frequency < other.frequency

    def __gt__(self, other):
        """
            Help decide about order of inserting to Priority Queue
            based on frequency of occurrences:
                return True if other is lower
        """
        return self.frequency > other.frequency

    def __eq__(self, other):
        """Determine if two Nodes are equal"""
        if not isinstance(self, other.__class__):
            return False
        return self.char == other.char and self.frequency == other.frequency

    def __ne__(self, other):
        """Determine if two Nodes are not equal"""
        return not self.__eq__(other)

    def is_leaf(self):
        return self.left is None and self.right is None
