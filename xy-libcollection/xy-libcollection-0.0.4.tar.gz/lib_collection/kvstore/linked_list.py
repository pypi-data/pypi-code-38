class LinkedListNode(object):

    def __init__(self, k, v):
        self.k = k
        self.v = v
        self.next = None

    def __repr__(self):
        """
        >>> n = LinkedListNode('a', 1)
        >>> n
        Node('a', 1)
        """
        return 'Node({}, {})'.format(repr(self.k), self.v)


class LinkedListKVstore(object):
    
    def __init__(self):
        self.length = 0
        self.head = LinkedListNode(None, None)

    def __len__(self):
        return self.length

    def __setitem__(self, k, v):
        """
        >>> link = LinkedListKVstore()
        >>> link['a'] = 1
        >>> link['b'] = 2
        >>> len(link)
        2
        >>> link['a']
        1
        >>> link['b'] 
        2
        >>> link['a'] = 100
        >>> link['a']
        100
        """
        h = self._get_node(k)
        if h is not None:
            h.v = v
        else:
            n = LinkedListNode(k, v)
            n.next = self.head.next
            self.head.next = n
            self.length += 1

    def _get_node(self, k):
        h = self.head.next
        while h:
            if h.k == k:
                return h 
            h = h.next

    def __getitem__(self, k):
        """
        >>> link = LinkedListKVstore()
        >>> link['a'] = 1
        >>> link['b'] = 2
        >>> len(link)
        2
        >>> link['a']
        1
        >>> link['b'] 
        2
        """
        h = self._get_node(k)
        if h is not None:
            return h.v

    def __delitem__(self, k):
        """
        >>> link = LinkedListKVstore()
        >>> link['a'] = 1
        >>> link['b'] = 2
        >>> link['c'] = 3
        >>> len(link)
        3
        >>> del link['b']
        >>> len(link)
        2
        """
        h = self.head
        while h.next:
            if h.next.k == k:
                h.next = h.next.next
                self.length -= 1
                return
            h = h.next

    def __repr__(self):
        """
        >>> link = LinkedListKVstore()
        >>> link['a'] = 1
        >>> link['b'] = 2
        >>> link['c'] = 3
        >>> link
        {'c': 3, 'b': 2, 'a': 1}
        """
        k_v = ['{}: {}'.format(repr(k), v) for k, v in self]
        return '{' + ', '.join(k_v) + '}'

    def __iter__(self):
        """
        >>> link = LinkedListKVstore()
        >>> link['a'] = 1
        >>> link['b'] = 2
        >>> link['c'] = 3
        >>> for k, v in link:
        ...     print(k, v)
        c 3
        b 2
        a 1
        """
        h = self.head.next
        while h:
            yield h.k, h.v
            h = h.next

    def __contains__(self, k):
        """
        >>> link = LinkedListKVstore()
        >>> link['a'] = 1
        >>> link['b'] = 2
        >>> 'a' in link
        True
        >>> 'c' in link
        False
        """
        h = self._get_node(k)
        return h is not None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
