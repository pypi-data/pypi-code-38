class LinkedListNode(object):
    def __init__(self, k, v):
        self.k = k
        self.v = v
        self.next = None

    def __repr__(self):
        """
        >>> node = LinkedListNode('a', 1)
        >>> node
        'a': 1
        """
        return "'{}': {}".format(self.k, self.v)


class LinkedListKVStore(object):

    def __init__(self):
        self.head = LinkedListNode(None, None)
        self.n = 0

    def __len__(self):
        """
        >>> d = LinkedListKVStore()
        >>> d['a'] = 1
        >>> len(d)
        1
        >>> d['b'] = 2
        >>> d['a'] = 3
        >>> len(d)
        2
        """
        return self.n

    def __setitem__(self, k, v):
        """
        >>> d = LinkedListKVStore()
        >>> d['a'] = 1
        """
        node = self._get_node(k)
        if node:
            node.v = v
        else:
            new_node = LinkedListNode(k, v)
            new_node.next = self.head.next
            self.head.next = new_node
            self.n += 1

    def __getitem__(self, k):
        """
        >>> d = LinkedListKVStore()
        >>> d['a'] = 1
        >>> d['a']
        1
        >>> d['b'] = 2
        >>> d['a'] = 3  # test update
        >>> d['a']
        3
        """
        node = self._get_node(k)
        return None if node is None else node.v

    def __contains__(self, k):
        """
        >>> d = LinkedListKVStore()
        >>> d['a'] = 1
        >>> 'a' in d
        True
        >>> 'b' in d
        False
        """
        return self._get_node(k) is not None

    def __delitem__(self, k):
        """
        >>> d = LinkedListKVStore()
        >>> d['a'] = 1
        >>> 'a' in d
        True
        >>> len(d)
        1
        >>> del d['a']
        >>> 'a' in d
        False
        >>> len(d)
        0
        """
        h = self.head
        while h.next:
            if h.next.k == k:
                h.next = h.next.next
                self.n -= 1
                return
            h = h.next

    def __repr__(self):
        """
        >>> d = LinkedListKVStore()
        >>> d['a'] = 1
        >>> d['b'] = 2
        >>> d['c'] = 3
        >>> d
        {'c': 3, 'b': 2, 'a': 1}
        """
        k_v = ["'{}': {}".format(k, v) for k, v in self]
        return '{' + ', '.join(k_v) + '}'

    def __iter__(self):
        """
        >>> d = LinkedListKVStore()
        >>> d['a'] = 1
        >>> d['b'] = 2
        >>> d['c'] = 3
        >>> for k, v in d:
        ...     print k, v
        ...
        c 3
        b 2
        a 1
        """
        h = self.head.next
        while h:
            yield h.k, h.v
            h = h.next

    # private methods

    def _get_node(self, k):
        n = self.head.next
        while n:
            if n.k == k:
                return n
            n = n.next
