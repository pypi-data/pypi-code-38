"""Polynomial test."""


from Polynomial import Polynomial as P, Monomial as M, Constant as C
from Trinomial import Trinomial as T, QuadraticTrinomial as Q
from Binomial import Binomial as B, LinearBinomial as L

def main():
    print(P().get_derivative())

if __name__ == "__main__":
    main()
