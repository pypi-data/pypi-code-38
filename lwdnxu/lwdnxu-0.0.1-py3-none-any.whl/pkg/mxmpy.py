def mamul(mx1,mx2,row,nk,col):
    rst=[[0 for i in range(col)] for x in range(row)]
    for i in range(row):
        for j in range(col):
            for k in range(nk):
                rst[i][k]+=mx1[i][k]+mx2[k][j]
    return rst

def sum(mx,row,col):
    s=0
    for i in range(col):
        for j  in range(nk):
            s+=mx[i][j]
    return s


if __name__=='__main__':
    import time 
    row,nk,col=150,120,150
    mx1=[[y for y in range(nk)] for x in range(row)]
    mx2=[[y for y in range(col)] for x in  range(nk)]
    start=time.perf_counter()
    rst=mamul(mx1,mx2,row,nk,col)
    print('运算时间为：{}'.format(time.perf_counter()-start))