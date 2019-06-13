from itertools import combinations,permutations

def add_rollup(dic,group,prefix,division,d_index,redundant):
    for k in range(d_index,prefix,-1):
        if division and division>=k:
                division=None
        if not division:
            for i in range(k):
                key=tuple(group[:i])
                if key not in dic:
                    dic[key]=set()
                v=group[i:k]
                if v not in dic[key]:
                    dic[key].add(v)
                else:
                    if key not in redundant:
                        redundant[key]=set()
                    redundant[key].add(v)
        else:
            key=tuple(group[:division])
            if key not in dic:
                dic[key]=set()
            v=group[division:k]
            if v not in dic[key]:
                dic[key].add(v)
            else:
                if key not in redundant:
                    redundant[key]=set()
                redundant[key].add(v)

#when there are n numbers and group, return the next available for group[-1]
def nextnum(group,n):
    res=(group[-1]+1)%n
    if len(group)>1:
        while res in group[:-1]:
            res=(res+1)%n
    return res

#find the prefix that we want to do regression for this group. If a prefix
#will be taken care of by a different grouping, then not do it.            
def findpre(group,d_index,n):
    for k in range(d_index,0,-1):
        if group[k]!=nextnum(group[:k],n):
            return k
    return 0

def main():
    n=8
    l=[i for i in range(n)]
    
    all_group={}
    for i in range(4,0,-1):
        groups=combinations(l,i)
        for group in groups:
            for j in range(len(group),0,-1):
                vs=combinations(group,j)
                for v in vs:
                    f=tuple(sorted([f for f in group if f not in v]))
                    if f not in all_group:
                        all_group[f]=set()
                    all_group[f].add(v)
    
    perm_group={}
    redundant={}
    combs=combinations(l,min(4,len(l)))
    for comb in combs:
        perms=permutations(comb,len(comb))
        for perm in perms:
            decrease=0
            d_index=None
            division=None
            for i in range(1,len(perm)):
                if perm[i-1]>perm[i]:
                    decrease+=1
                    if decrease==1:
                        division=i
                if decrease==2:
                    d_index=i #perm[:d_index] will decrease at most once
                    
            if not d_index:
                d_index=len(perm)
                pre=findpre(perm,d_index-1,n)
            else:
                pre=findpre(perm,d_index,n)
            
            if pre==d_index:
                continue
            else:
                add_rollup(perm_group,perm,pre,division,d_index,redundant)
            
    dif={}
    for key in all_group:
        if key not in perm_group:
            dif[key]=all_group[key]
        else:
            for v in all_group[key]:
                if v not in perm_group[key]:
                    if key not in dif:
                        dif[key]=set()
                    dif[key].add(v)
    
    print(dif)
    print(redundant)

if __name__=="__main__":
    main()
