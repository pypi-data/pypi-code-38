import pandas as pd
from tabletree import __version__

__author__ = "Xi Rossi LUO"
__copyright__ = "Xi Rossi LUO"
__license__ = "GPLv3"

class TableNode:
    """Node for holding tables
    should have upper-stream nodes (parent) or lower-stream nodes (children)
    It can have multiple children but only 1 parent (not fully implemented yet)
    """
    def __init__(self, name,  df,  parent=None, children=None, plink=None, clink=None):
        self.name = name
        self.parent = parent  # should be a ref to parent DN
        self.children = children # ref to children DN
        self.df = df  ## pandas data frame, first column is the unique id
        self.plink = plink ## DataLink object
        self.clink = clink

class TableLink:
    """Linking Data Nodes together
    should be a one-to-one link  
    """
    def __init__(self, fromid, toid):
        self.fromid = fromid ## string
        self.toid = toid
    
    def reversed(self):
        return TableLink(self.toid, self.fromid)

class TableTree:
    def __init__(self, rootDN):
        self.root = rootDN

    def addChildren(self, newDN, datalink):
        cur = self.root
        while (cur.children != None):
            cur = cur.children
        cur.children = newDN
        cur.clink = datalink
        cur.children.plink = datalink.reversed()
        cur.children.parent = cur
        TableTree.checkDataLink(cur, cur.children, datalink)
        
    def getAncestors(self, name):
        ret = []
        cur = self.root
        while cur.children:
            if cur.name == name:
                return ret
            else:
                ret.append(cur.name)
                cur = cur.children
        return ret
    
    def getOffsprings(self, name):
        ret = []
        cur = self.root
        start = 0
        while cur:
            if cur.name == name:
                ret = []
                start = 1
            else:
                if start:
                    ret.append(cur.name)
            cur = cur.children
        return ret

    def reset(self):
        cur = self.root
        while cur.children:
            cDN = cur
            cur = cur.children
            cDN.plink = None
            cDN.clink = None
            cDN.parent = None
            cDN.children = None
        return 1
        
    def getTN(self, name):
        cur = self.root
        while cur:
            if cur.name == name:
                return cur
            else:
                cur = cur.children
        return None
               
    def findMatched(self, retDNname, matchDNname, matchsel):
        ## sel can be boolean list
        mDN = self.getTN(matchDNname)
        ancesters = self.getAncestors(retDNname)
        offsprings = self.getOffsprings(retDNname)
        # match df parents of ret df, proporgate down
        if matchDNname in ancesters:
            nlevels = len(ancesters) - ancesters.index(matchDNname)
            for _ in range(nlevels):
                idlist = TableTree.propogate(mDN, matchsel, up=False)
                toid = mDN.clink.toid
                mDN = mDN.children
                matchsel = mDN.df[toid].isin(idlist)
        elif matchDNname in offsprings:
            nlevels = offsprings.index(matchDNname) + 1
            for _ in range(nlevels):
                idlist = TableTree.propogate(mDN, matchsel, up=True)
                toid = mDN.plink.toid
                mDN = mDN.parent
                print(mDN)
                matchsel = mDN.df[toid].isin(idlist)
        else:
            print(matchDNname + " not in tree!")
            raise ValueError
        return mDN.df.loc[matchsel]      
        
    @staticmethod    
    def propogate(fromDN, from_df_rowsel, up=True):
        if up:
            return fromDN.df.loc[from_df_rowsel][fromDN.plink.fromid]
        else:
            return fromDN.df.loc[from_df_rowsel][fromDN.clink.fromid]
        
        
    @staticmethod
    def checkDataLink(fromDN, toDN, datalink):
        if not datalink.fromid in fromDN.df.columns:
            print('from id not exist in {}'.format(fromDN.name))
            raise ValueError
        if not datalink.toid in toDN.df.columns:
            print('to id not exist in {}'.format(toDN.name))
            raise ValueError