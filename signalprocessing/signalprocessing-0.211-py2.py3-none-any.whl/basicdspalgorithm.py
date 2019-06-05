class basicdspalgorithm:

      
    # parameterized constructor 
    def __init__(self):
        self.first = 0 
        self.second= 0
    def conv(self,x,h): 
        self.first=x
        self.second=h
        N=len(self.first)+len(self.second)-1
        x1=[0]*N
        h1=[0]*N
        m=len(self.first)
        n=len(self.second)
        self.answer=[0]*N
        for i in range(m):
            x1[i]=self.first[i]    
        for i in range(n):
            h1[i]=self.second[i]
        
        for i in range(N):
            for j in range(i+1):
                self.answer[i]=self.answer[i]+ x1[j]*h1[i-j]
        
        return self.answer
    
    def circonv(self,x,h):
        import operator as op
        #self.first=x
        #self.second=h
        N=max(len(x),len(h))
        y=[0]*N
        x1=[0]*N
        h1=[0]*N
        for i in range(len(x)):
            x1[i]=x[i]
        for i in range(len(h)):
            h1[i]=h[i]
        for i in range(N):
            for j in range(N):
                y[i]=y[i]+x1[j]*h1[op.mod((i-j),N)]

        return y
    
    def fft(self,x):
        import cmath as mt
        N=len(x)
        X=[0]*N
        for k in range(N):
            for n in range(N):
                X[k]=X[k] + x[n]*mt.exp(-1j*2*mt.pi*k*n/N)
        return X
    
    def auto(self,x):
        x1=x[::-1]
        N=len(x)+len(x1)-1
        x11=[0]*N
        h1=[0]*N
        m=len(x)
        n=len(x1)
        y=[0]*N
        for i in range(m):
            x11[i]=x[i]    
        for i in range(n):
            h1[i]=x1[i]   
        for i in range(N):
            for j in range(i+1):
                y[i]=y[i]+ x11[j]*h1[i-j]   
        return y

    def cross(self,x,h):
        h1=h[::-1]
        N=len(x)+len(h)-1
        x11=[0]*N
        h11=[0]*N
        m=len(x)
        n=len(h)
        y=[0]*N
        for i in range(m):
            x11[i]=x[i]    
        for i in range(n):
            h11[i]=h1[i]   
        for i in range(N):
            for j in range(i+1):
                y[i]=y[i]+ x11[j]*h11[i-j]   
        return y