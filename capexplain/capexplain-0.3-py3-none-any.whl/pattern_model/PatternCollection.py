"""
Data structures for representing aggregate regression patterns (ARPs).
"""

"""
Represents a global pattern (F, V, g)
"""
class GlobalPattern(object):
    
    def __init__(self, f, v, model, theta, lamb):
        self.f = f
        self.v = v
        self.model = model
        self.theta = theta
        self.lamb = lamb
        

class LocalPattern(object):
    
    def __init__(self, f, f_value, v, model, theta):
        self.f = f
        self.f_value = f_value
        self.v = v
        self.model = model
        self.theta = theta

class SetTrie(object):

    def __init__(self):
        self.root = TrieEntry()
        
    def search(self, attr):
        """
        :param attr: list of sorted int
        :return: 2 lists of patterns
        """
        cur=self.root
        for i in attr:
            if i not in cur.child:
                return None, None
            cur=cur.child[i]
        else:
            return cur.l, cur.g

    def search_subset(self, attr):
        loc = []
        glob = []
        self.__search_subset(self.root, attr, 0, loc, glob)
        return loc, glob

    def __search_subset(self, te, attr, start, loc, glob):
        for i in range(start,len(attr)):
            if attr[i] in te.child:
                ne = te.child[attr[i]]
                if ne.l:
                    loc+=ne.l
                if ne.g:
                    glob+=ne.g
                self.__search_subset(ne, attr, i+1, loc, glob)


class TrieEntry(object):
    """
        Attributes:
            child: dictionary that points to the group that has G
                      as prefix
            g: list of global patterns under the group
            l: list of local patterns under the group
    """
    def __init__(self):
        self.g = None
        self.l = None
        self.child = {}


class PatternCollection(object):
    """
        Attributes:
            header: list of attribute names
            index: dict that maps attribute names to their index in header
            a: list of dictionaries. Each index is an attr, and each
               dictionary maps an aggregate function to the root of the
               trie that stores patterns
    """
    
    def __init__(self, header):
        """
        type header: list of strings
        """
        self.header = header
        self.index={}
        for i in range(len(header)):
            self.index[header[i]] = i
        self.a = [{} for i in range(len(header))]
        
    def search(self, a, attr, agg):
        """
        type a: string
        type attr: list of strings
        type agg: string
        """
        return self.a[self.index[a]][agg].search([self.index[i] for i in attr].sort())

    def search_subset(self, a, attr, agg):

        return self.a[self.index[a]][agg].search_subset([self.index[i] for i in attr].sort())

    def add_global(self, f, v, a, agg, model, theta, lamb):
        """      
            type f: list of strings
            type v: list of strings
            type a: string
            type agg: string
            model: string
            theta: float
            lamb: float
        """
        a=self.index[a]
        f=[self.index[i] for i in f]
        v=[self.index[j] for j in v]
        attr=sorted(f+v)
        if agg not in self.a[a]:
            self.a[a][agg]=SetTrie()
        cur=self.a[a][agg].root
        for i in attr:
            if i not in cur.child:
                cur.child[i]=TrieEntry()
            cur=cur.child[i]
        if not cur.g:
            cur.g=[]
        cur.g.append(GlobalPattern(f,v,model,theta,lamb))
    
    def add_local(self, f, f_value, v, a, agg, model, theta):
        a=self.index[a]
        f=[self.index[i] for i in f]
        v=[self.index[j] for j in v]
        attr=sorted(f+v)
        if agg not in self.a[a]:
            self.a[a][agg]=SetTrie()
        cur=self.a[a][agg].root
        for i in attr:
            if i not in cur.child:
                cur.child[i]=TrieEntry()
            cur=cur.child[i]
        if not cur.l:
            cur.l=[]
        cur.l.append(LocalPattern(f,f_value,v,model,theta))
    
