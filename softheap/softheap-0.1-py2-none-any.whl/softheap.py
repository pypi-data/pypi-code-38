# https://www.cs.princeton.edu/~chazelle/pubs/sheap.pdf

import math

class SoftHeap:

    class ilcell:

        def __init__(self):
            # int
            self.key = 0
            # ilcell
            self.next = None

        def set_key(self, value):
            assert type(
                value) is int, "Error @ ilcell.set_key: Value passed into set_key must be of type int; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.key = value

        def get_key(self):
            return self.key

        def set_next(self, value):
            assert type(value) is SoftHeap.ilcell, "Error @ ilcell.set_next: Value passed into set_next must be of type ilcell; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.next = value

        def get_next(self):
            return self.next

    class node:

        def __init__(self):
            # int
            self.ckey = 0
            # int
            self.rank = 0
            # node
            self.next = None
            # node
            self.child = None
            # ilcells
            self.il = None
            # ilcells
            self.il_tail = None

        def set_ckey(self, value):
            assert type(
                value) is int or value == math.inf, "Error @ node.set_ckey: Value passed into set_ckey must be of type int; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.ckey = value

        def get_ckey(self):
            return self.ckey

        def set_rank(self, value):
            assert type(
                value) is int, "Error @ node.set_rank: Value passed into set_rank must be of type int; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.rank = value

        def get_rank(self):
            return self.rank

        def set_next(self, value):
            assert type(
                value) is SoftHeap.node or value == None, "Error @ node.set_next: Value passed into set_next must be of type node; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.next = value

        def get_next(self):
            return self.next

        def set_child(self, value):
            assert type(
                value) is SoftHeap.node or value == None, "Error @ node.set_child: Value passed into set_child must be of type node; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.child = value

        def get_child(self):
            return self.child

        def set_il(self, value):
            assert type(
                value) is SoftHeap.ilcell or value == None, "Error @ node.set_il: Value passed into set_il must be of type ilcell; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.il = value

        def get_il(self):
            return self.il

        def set_il_tail(self, value):
            assert type(
                value) is SoftHeap.ilcell or value == None, "Error @ node.set_il_tail: Value passed into set_il_tail must be of type ilcell; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.il_tail = value

        def get_il_tail(self):
            return self.il_tail

    class head:

        def __init__(self):
            # node
            self.queue = None
            # head
            self.next = None
            # head
            self.prev = None
            # head
            self.suffix_min = None
            # int
            self.rank = 0

        def set_queue(self, value):
            assert type(
                value) is SoftHeap.node, "Error @ head.set_queue: Value passed into method must be of type node; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.queue = value

        def get_queue(self):
            return self.queue

        def set_next(self, value):
            assert type(
                value) is SoftHeap.head, "Error @ head.set_next: Value passed into method must be of type head; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.next = value

        def get_next(self):
            return self.next

        def set_prev(self, value):
            assert type(
                value) is SoftHeap.head, "Error @ head.set_prev: Value passed into method must be of type head; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.prev = value

        def get_prev(self):
            return self.prev

        def set_suffix_min(self, value):
            assert type(
                value) is SoftHeap.head, "Error @ head.set_suffix_min: Value passed into method must be of type head; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.suffix_min = value

        def get_suffix_min(self):
            return self.suffix_min

        def set_rank(self, value):
            assert type(
                value) is int or value == math.inf, "Error @ head.set_rank: Value passed into set_rank must be of type int; received value " + str(
                value) + " of type " + str(type(value)) + "."

            self.rank = value

        def get_rank(self):
            return self.rank

    def __init__(self, r):
        assert type(
            r) is int, "Error @ SoftHeap.__init__: Value 'r' passed into constructor must be of type int; received value " + str(
            r) + " of type " + str(type(r)) + "."

        # head
        self.header = self.head()
        # head
        self.tail = self.head()

        self.tail.set_rank(math.inf)

        self.header.set_next(self.tail)

        self.tail.set_prev(self.header)
        # int
        self.r = r

    def insert(self, newkey):

        assert type(
            newkey) is int, "Error @ SoftHeap.insert: Key passed into insert must be of type int; received value " + str(
            newkey) + " of type " + str(type(newkey)) + "."

        # ilcell
        l = self.ilcell()
        l.set_key(newkey)

        q = self.node()

        q.set_rank(0)

        q.set_ckey(newkey)

        q.set_il(l)

        q.set_il_tail(l)

        self.meld(q)

    def meld(self, q):  # q is node

        assert type(
            q) is SoftHeap.node, "Error @ SoftHeap.meld: Value 'q' passed into method must be of type node; received value " + str(
            q) + " of type " + str(type(q)) + "."

        # head
        h = self.head()
        # head
        prevhead = self.head()
        # head
        tohead = self.header.get_next()
        # node
        top = self.node()
        # nodself.e
        bottom = self.node()

        while q.get_rank() > tohead.get_rank():
            tohead = tohead.get_next()

        prevhead = tohead.get_prev()

        while q.get_rank() == tohead.get_rank():

            if tohead.get_queue().get_ckey() > q.get_ckey():
                top = q
                bottom = tohead.get_queue()
            else:
                top = tohead.get_queue()
                bottom = q

            q = self.node()
            q.set_ckey(top.get_ckey())
            q.set_rank(top.get_rank() + 1)
            q.set_child(bottom)
            q.set_next(top)
            q.set_il(top.get_il())
            q.set_il_tail(top.get_il_tail())
            tohead = tohead.get_next()

        if prevhead == tohead.get_prev():
            h = self.head()
        else:
            h = prevhead.get_next()

        h.set_queue(q)
        h.set_rank(q.get_rank())
        h.set_prev(prevhead)
        h.set_next(tohead)
        prevhead.set_next(h)
        tohead.set_prev(h)

        self.fix_minlist(h)

    def fix_minlist(self, h):  # head

        assert type(
            h) is SoftHeap.head, "Error @ SoftHeap.fix_minlist: Value 'h' passed into method must be of type head; received value " + str(
            h) + " of type " + str(type(h)) + "."

        if h.get_next() == self.tail:
            tmpmin = h
        else:
            tmpmin = h.get_next().get_suffix_min()

        while h != self.header:
            if h.get_queue().get_ckey() < tmpmin.get_queue().get_ckey():
                tmpmin = h
            h.set_suffix_min(tmpmin)
            h = h.get_prev()

    def sift(self, v):

        assert type(
            v) is SoftHeap.node, "Error @ SoftHeap.sift: Value 'v' passed into method must be of type node; received value " + str(
            v) + " of type " + str(type(v)) + "."

        v.set_il(None)
        v.set_il_tail(None)

        if v.get_next() == None and v.get_child() == None:
            v.set_ckey(math.inf)
            return v

        else:
            v.set_next(self.sift(v.get_next()))

            if v.get_next().get_ckey() > v.get_child().get_ckey():
                tmp = v.get_child()
                v.set_child(v.get_next())
                v.set_next(tmp)

            v.set_il(v.get_next().get_il())
            v.set_il_tail(v.get_next().get_il_tail())
            v.set_ckey(v.get_next().get_ckey())

            if v.get_rank() > self.r and (v.get_rank() % 2 == 1 or v.get_child().get_rank() < v.get_rank() - 1):
                v.set_next(self.sift(v.get_next()))

                if v.get_next().get_ckey() > v.get_child().get_ckey():
                    tmp = v.get_child()
                    v.set_child(v.get_next())
                    v.set_next(tmp)

                if v.get_next().get_ckey() != math.inf and v.get_next().get_il() != None:
                    v.get_next().get_il_tail().set_next(v.get_il())
                    v.set_il(v.get_next().get_il())
                    if v.get_il_tail() == None:
                        v.set_il_tail(v.get_next().get_il_tail())
                    v.set_ckey(v.get_next().get_ckey())

            if v.get_child().get_ckey() == math.inf:

                if v.get_next().get_ckey() == math.inf:
                    v.set_child(None)
                    v.set_next(None)
                else:
                    v.set_child(v.get_next().get_child())
                    v.set_next(v.get_next().get_next())

            return v

    def deletemin(self):
        # head
        h = self.header.get_next().get_suffix_min()
        while h.get_queue().get_il() == None:
            tmp = h.get_queue()
            # int
            childcount = 0

            while tmp.get_next() != None:
                tmp = tmp.get_next()
                childcount += 1

            if childcount < int(h.get_rank() / 2):
                h.get_prev().set_next(h.get_next())
                h.get_next().set_prev(h.get_prev())
                self.fix_minlist(h.get_prev())
                tmp = h.get_queue()
                while tmp.get_next() != None:
                    self.meld(tmp.get_child())
                    tmp = tmp.get_next()
            else:
                h.set_queue(self.sift(h.get_queue()))

                if h.get_queue().get_ckey() == math.inf:
                    h.get_prev().set_next(h.get_next())
                    h.get_next().set_prev(h.get_prev())
                    h = h.get_prev()
                self.fix_minlist(h)
            h = self.header.get_next().get_suffix_min()

        min = h.get_queue().get_il().get_key()
        h.get_queue().set_il(h.get_queue().get_il().get_next())
        if h.get_queue().get_il() == None:
            h.get_queue().set_il_tail(None)
        return min










