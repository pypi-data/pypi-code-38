import numpy as np


def area_under_curve(x, y, x_start, x_end):
    x_new, y_new = xy_with_endpoints(x, y, x_start, x_end)
    res = np.trapz(y=y_new, x=x_new)
    return res


def xy_with_endpoints(x, y, x_start, x_end):
    if x_start <= x[0]:
        x_start = x[0]

    if x_end >= x[-1]:
        x_end = x[-1]

    # Για την αρχή
    y_start = float(np.interp(x_start, x, y))
    # Κρατώ μόνο τις τιμές μετά από το x_start
    _x = x[(x > x_start)]
    _y = y[len(y) - len(_x):len(y)]
    # Προσθέτω τα x, y της παρεμβολής
    _x = np.append(x_start, _x)
    _y = np.append(y_start, _y)

    # Για το τέλος
    y_end = float(np.interp(x_end, x, y))
    # Κρατώ μόνο τις τιμές μέχρι μία πρίν από το x_end
    _x = _x[(_x < x_end)]
    _y = _y[0:len(_x)]
    # Προσθέτω τα x, y της παρεμβολής
    _x = np.append(_x, x_end)
    _y = np.append(_y, y_end)

    return _x, _y


def _rect_inter_inner(x1,x2):
    n1=x1.shape[0]-1
    n2=x2.shape[0]-1
    X1=np.c_[x1[:-1],x1[1:]]
    X2=np.c_[x2[:-1],x2[1:]]
    S1=np.tile(X1.min(axis=1),(n2,1)).T
    S2=np.tile(X2.max(axis=1),(n1,1))
    S3=np.tile(X1.max(axis=1),(n2,1)).T
    S4=np.tile(X2.min(axis=1),(n1,1))
    return S1,S2,S3,S4

def _rectangle_intersection_(x1,y1,x2,y2):
    S1,S2,S3,S4=_rect_inter_inner(x1,x2)
    S5,S6,S7,S8=_rect_inter_inner(y1,y2)

    C1=np.less_equal(S1,S2)
    C2=np.greater_equal(S3,S4)
    C3=np.less_equal(S5,S6)
    C4=np.greater_equal(S7,S8)

    ii,jj=np.nonzero(C1 & C2 & C3 & C4)
    return ii,jj


def intersection(x1,y1,x2,y2):
    """Copied from https://github.com/sukhbinder/intersection

        INTERSECTIONS Intersections of curves.
        Computes the (x,y) locations where two curves intersect.  The curves
        can be broken with NaNs or have vertical segments.

        .. usage:
            x,y=intersection(x1,y1,x2,y2)
            Example:
                a, b = 1, 2
                phi = np.linspace(3, 10, 100)
                x1 = a*phi - b*np.sin(phi)
                y1 = a - b*np.cos(phi)
                x2=phi
                y2=np.sin(phi)+2
                x,y=intersection(x1,y1,x2,y2)
                plt.plot(x1,y1,c='r')
                plt.plot(x2,y2,c='g')
                plt.plot(x,y,'*k')
                plt.show()
    """
    ii, jj = _rectangle_intersection_(x1, y1, x2, y2)
    n=len(ii)

    dxy1=np.diff(np.c_[x1,y1],axis=0)
    dxy2=np.diff(np.c_[x2,y2],axis=0)

    T=np.zeros((4,n))
    AA=np.zeros((4,4,n))
    AA[0:2,2,:]=-1
    AA[2:4,3,:]=-1
    AA[0::2,0,:]=dxy1[ii,:].T
    AA[1::2,1,:]=dxy2[jj,:].T

    BB=np.zeros((4,n))
    BB[0,:]=-x1[ii].ravel()
    BB[1,:]=-x2[jj].ravel()
    BB[2,:]=-y1[ii].ravel()
    BB[3,:]=-y2[jj].ravel()

    for i in range(n):
        try:
            T[:,i]=np.linalg.solve(AA[:,:,i],BB[:,i])
        except:
            T[:,i]=np.NaN


    in_range= (T[0,:] >=0) & (T[1,:] >=0) & (T[0,:] <=1) & (T[1,:] <=1)

    xy0=T[2:,in_range]
    xy0=xy0.T
    return xy0[:,0],xy0[:,1]