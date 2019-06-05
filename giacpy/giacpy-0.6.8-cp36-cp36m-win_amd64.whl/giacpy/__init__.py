#*****************************************************************************
#    AUTHOR:  Han Frederic <han@math.jussieu.fr>
#  2012
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************
"""giacpy: Interface to the C++ library giac (Computer Algebra System).

Giac is a general computer algebra system created by Bernard Parisse.
Homepage http://www-fourier.ujf-grenoble.fr/~parisse/giac.html


The natural way to use giacpy is through the giac function. This function
creates a Pygen object and evaluate it with the giac C++ library.

The initialisation of a Pygen just create an object in the C++ library
giac, but the mathematical computation  is not done. This class is mainly
usefull for cython users.

EXAMPLES::

    >>> import giacpy    # giacpy doesn't need aide_cas
    Help file ...aide_cas not found
    Added 0 synonyms
    >>> giacpy.ifactor(2**128+1)
    59649589127497217*5704689200685129054721
    >>> from giacpy import giac
    >>> x,y,z=giac('x,y,z');  # add some giac objects
    >>> f=(x+3*y)/(x+z+1)**2 -(x+z+1)**2/(x+3*y)
    >>> f.factor()
    (3*y-x**2-2*x*z-x-z**2-2*z-1)*(3*y+x**2+2*x*z+3*x+z**2+2*z+1)/((x+z+1)**2*(3*y+x))
    >>> f.normal()    # doctest: +ELLIPSIS
    (-x**4-4*x**3*z-4*x**3-6*x**2*z**2-12*x**2*z-5*x**2+...2*x*z+x+3*y*z**2+6*y*z+3*y)

. To obtain more hints on giacpy consider the help of the giac function.

    >>> help(giac)             # doctest: +SKIP

GETTING HELP::

#. To obtain some help on a giac keyword use __doc__ attribute.

    >>> from giacpy import *
    >>> print(gcd.__doc__)              # doctest: +SKIP
    "Returns the greatest common divisor of 2 polynomials of several variables...
    (Intg or Poly),(Intg or Poly)
    gcd(45,75);gcd(15/7,50/9);gcd(x^2-2*x+1,x^3-1);gcd(t^2-2*t+1,t^2+t-2);...
    lcm,euler,modgcd,ezgcd,psrgcd,heugcd,Gcd"

#. You can find full html documentation in several languages (en, fr, el) at:

   http://www-fourier.ujf-grenoble.fr/~parisse/giac/doc/en/cascmd_en/

   on linux you can try to open its local copy (if avaible) with the command:

    >>> from giacpy import htmlhelp
    >>> htmlhelp()        # doctest: +SKIP
    >>> htmlhelp('fr')    # doctest: +SKIP

#. You can import more giac keywords to work in a symbolic ring.

EXAMPLES::

    >>> from giacpy import *
    >>> x=giac('x');f=1/(2+sin(5*x))
    >>> f.int()
    2/5/sqrt(3)*(atan((2*tan(5*x/2)+1)/sqrt(3))+pi*floor(5*x/2/pi+1/2))
    >>> f.series(x,0,3)
    1/2-5/4*x+25/8*x**2-125/48*x**3+x**4*order_size(x)
    >>> (sqrt(5)+pi).approx(100)   # doctest: +ELLIPSIS
    5.3776606310895829348718170520107791196377877589866...2449233720899343

#. Cas Settings. Some convienent settings are obtained from: giacsettings:

    >>> from giacpy import giacsettings


#. Graphics 2D Output. If your version of giacpy is built with Qt support,
you can send graphics to qcas. For experimental interactive geometry see:
help(qcas)

EXAMPLES::

    >>> from giacpy import *
    >>> C=giac('plot(x*sin(x)),x=-3*pi,3*pi')
    >>> C.qcas()             # doctest: +SKIP
    >>> l=[(C*t*0.1).color(t) for t in range(10)]
    >>> giac(l).qcas)        # doctest: +SKIP
    >>> A=randvector(200)
    >>> (histogram(classes(A,0,10))).qcas()         # doctest: +SKIP
    >>> C=giac('plot(sin(x)/x),x=-3*pi,3*pi')
    >>> C.qcas()             # doctest: +SKIP
    >>> l=[(C*t*0.1).color(t) for t in range(10)]
    >>> giac(l).qcas()       # doctest: +SKIP


"""
#
from sys import version_info as Pyversioninfo
if Pyversioninfo[0]<3 :
    from giacpy import *
    import giacpy
    __doc__ = giacpy.__doc__

else:
    #for python3
    from giacpy.giacpy import *
    import giacpy.giacpy
    __doc__ = giacpy.giacpy.__doc__
