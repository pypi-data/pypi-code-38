def closure(fd,n,a):
    '''
    return the closure of a, attributes are represented as corresponding integer indices in all schema
    type fd: list of tuple where each tuple = (lhs,rhs) where lhs,rhs are lists of int
    type n: length of all attributes
    type a: tuple/list/set of int
    '''
    if not a:
        return set()
    m=len(fd)
    c=[0]*m
    lhs=[[] for i in range(n)]
    rhs=[[] for i in range(m)]
    aplus=set()
    todo=list(a)
    
    for i in range(m):
        left=fd[i][0]
        right=fd[i][1]
        c[i]=len(left)
        for attr in left:
            lhs[attr].append(i)
        for attr in right:
            rhs[i].append(attr)
    
    while todo:
        curA=todo.pop()
        aplus.add(curA)
        for fd in lhs[curA]:
            c[fd]-=1
            if c[fd]==0:
                for newA in rhs[fd]:
                    if newA not in aplus:
                        todo.append(newA)
                        
    return aplus

def main():
    return
    
if __name__=="__main__":
    main()
    
