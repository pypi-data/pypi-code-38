"""
A module for collecting analytic Sympy methods.
"""


def knm_bayerhelms(n1, n2, q1, q2, lam=1064e-9, gamma=0):
    """
    Caclulates the 1D Bayer-Helms coupling coefficients for either tilt or mismatch.
    
    In relation to bayer helms notation
        1 == unprimed
        2 == primed
    """
    
    q1, q2 = symbols('q_1, q_2',complex=True)
    z1, z2, zR1, zR2 = symbols('z_1, z_2, z_{R1}, z_{R2}',real = True)
    gamma = symbols('gamma',real=True)
    w0 = symbols('w_0', positive=True)
    w1,w2 = symbols('w_1,w_2', positive=True)
    
    # # rip out subcomponents of q
    # z1 = re(q1)
    # z2 = re(q2)
    # zR1 = im(q1)
    # zR2 = im(q2)
    # w0 = sqrt(lam*zR1/pi)
    
    # Bayer-Helms sub terms (use original paper, finesse manual gets F and F_bar wrong way around)
    K2 = (z1-z2)/zR2
    K0 = (zR1 - zR2)/zR2  
    K = I*conjugate(q1-q2)/(2*im(q2))
    K = (K0 + I*K2)/2
    X_bar = (I*zR2 - z2)*sin(gamma)/(sqrt(1+conjugate(K))*w0)
    X = (I*zR2 + z2)*sin(gamma)/(sqrt(1+conjugate(K))*w0)
    F_bar = K/(2*(1+K0))
    F = conjugate(K)/2
    E_x = exp(-(X*X_bar)/2)
    
    def S_g(n1,n2):
        s1 = 0
        for mu1 in range(0, (n1//2 if n1 % 2 == 0 else (n1-1)//2) + 1):
            for mu2 in range(0, (n2//2 if n2 % 2 == 0 else (n2-1)//2) + 1):
                t1 = ((-1)**mu1 * X_bar**(n1-2*mu1) * X**(n2-2*mu2))/(factorial(n1-2*mu1)*factorial(n2-2*mu2))
                s2 = 0
                for sigma in range(0,min(mu1,mu2)+1):
                    s2 += ((-1)**sigma * F_bar**(mu1-sigma) * F**(mu2-sigma))/(factorial(2*sigma)*factorial(mu1-sigma)*factorial(mu2-sigma))
                s1 += t1 * s2
        return s1

    def S_u(n1,n2):
        s1 = 0
        for mu1 in range(0, ((n1-1)//2 if (n1-1) % 2 == 0 else ((n1-1)-1)//2) + 1):
            for mu2 in range(0, ((n2-1)//2 if (n2-1) % 2 == 0 else ((n2-1)-1)//2) + 1):
                t1 = ((-1)**mu1 * X_bar**((n1-1)-2*mu1) * X**((n2-1)-2*mu2))/(factorial((n1-1)-2*mu1)*factorial((n2-1)-2*mu2))
                s2 = 0
                for sigma in range(0,min(mu1,mu2)+1):
                    s2 += ((-1)**sigma * F_bar**(mu1-sigma) * F**(mu2-sigma))/(factorial(2*sigma+1)*factorial(mu1-sigma)*factorial(mu2-sigma))
                s1 += t1 * s2
        return s1
    
    expr = (-1)**n2 * E_x * sqrt(factorial(n1)*factorial(n2)) \
    * (1 + K0)**(Rational(n1,2) + Rational(1,4)) * (1+conjugate(K))**(Rational(-(n1+n2+1),2)) \
    * (S_g(n1,n2) - S_u(n1,n2))
    
    return expr