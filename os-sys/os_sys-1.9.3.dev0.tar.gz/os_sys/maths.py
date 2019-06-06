# list_to_num makes a number from a list of digits

# num_to_list converts a number to a list of digits

# list_to_str makes a string from a list

# str_to_list makes a list from a string (the same as list() )

# divisors makes a list of all the divisors of a number

# permutations creates a list of all the permutations from a list or a string

# Fib(n) gives the n-th number from the fibinacci sequence

# fibo(n) gives a list of the first n numbers from the fibonacci sequence

# is_fibo(n) : True if a number is in the fibonacci sequence, else False

def list_to_num(gl):
    g = 0
    for c in gl: g = g * 10 + c
    return g

def num_to_list(g):
    gl = []
    while (g > 0):
        c = g%10
        gl = [c] + gl
        g = g//10
    return gl

def list_to_str(sl):
    s = ''
    for l in sl: s += l
    return s

def str_to_list(s):
    l = []
    for i in range(0,len(s)): l += s[i]
    return l

def divisors(g):
    ldelers = [1,g]
    max = int(g**.5)
    for i in range(2,max+1):
        if (g%i == 0):
            if (i*i == g): ldelers = ldelers + [i]
            else: ldelers = ldelers + [i] + [g//i]
    ldelers.sort()
    return ldelers

def voegin(l,x):
    r = []
    # l is lijst van lijsten, x is één element
    for hl in l:
        for i in range(0,len(hl)):
            h = hl[0:i] + [x] + hl[i:]
            if h not in r: r += [h]
        h = hl + [x]
        if h not in r: r += [h]
    return r

def permutations(l):
    s = []
    if type(l) == type('str'):
        s = 'str'
        l = str_to_list(l)
    ll = len(l)
    if ll == 1: r = [l]
    else: r = voegin(permutations(l[0:ll-1]),l[ll-1])
    if type(s) == type('str'):
        r2 = []
        for x in r: r2 += [list_to_str(x)]
        return r2
    else: return r

def Fib(n):
    f1 = 1
    f2 = 2
    for i in range(3,n):
        f3 = f1 + f2
        f1 = f2
        f2 = f3

    return f3

def fibo(n):
    l = [0,1]
    for i in range(2,n+1): l += [l[i-1] + l[i-2]]

    return l

def is_fibo(n):
    teken = int(n/abs(n))
    k1 = 5*n*n + 4
    k2 = 5*n*n - 4*teken
    wk1 = int(k1**.5)
    wk2 = int(k2**.5)
    
    return ( wk1*wk1 == k1 or wk2*wk2 == k2)

    
