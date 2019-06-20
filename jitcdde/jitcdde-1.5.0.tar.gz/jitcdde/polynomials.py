from sympy.abc import *
import sympy

p = (1-x) * ( (1-x) * (b*x + (a-c)*(2*x+1)) - d*x**2) + c

assert( p.subs(x,0) == a )
assert( p.subs(x,1) == c )
assert( p.diff(x).subs(x,0) == b )
assert( p.diff(x).subs(x,1) == d )

diff = ( (1-x)*(b-x*3*(2*a+b-2*c+d)) + d*x )
assert( diff.equals(p.diff(x)) )

# norm
X = sympy.integrate(p**2, (x,0,1))

# partial norm 1
sympy.integrate(p**2, (x,0,y))

# partial norm 2
X = sympy.integrate(p**2, (x,y,1))

syms = [X+"_"+Y for X in "abcd" for Y in "12"]
for sym in syms:
	exec("%s = sympy.Symbol('%s')" % (sym,sym))

p_1 = (1-x)*((1-x)*(b_1*x+(a_1-c_1)*(2*x+1))-d_1*x**2)+c_1
p_2 = (1-x)*((1-x)*(b_2*x+(a_2-c_2)*(2*x+1))-d_2*x**2)+c_2

# scalar product
X = sympy.integrate((p_1*p_2), (x,0,1))

# partial scalar products
sympy.integrate((p_1*p_2), (x,0,y))
X = sympy.integrate((p_1*p_2), (x,y,1))

# symmetrising
q = p.subs(x, (z+1)/2).subs(b,2*b).subs(d,2*d)
q_1 = p_1.subs(x, (z+1)/2).subs(b_1,2*b_1).subs(d_1,2*d_1)
q_2 = p_2.subs(x, (z+1)/2).subs(b_2,2*b_2).subs(d_2,2*d_2)



Y = X.subs(y, z+1).expand()*420

v_1 = sympy.Matrix([a_1,b_1,c_1,d_1])
v_2 = sympy.Matrix([a_2,b_2,c_2,d_2])

A = sympy.Matrix([[Y.diff(p,q) for p in v_1] for q in v_2])

print (((v_1.T*A*v_2/420)[0].subs(z,y-1)-X).expand())
