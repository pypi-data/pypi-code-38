from math import pi


def area_circle(r):
    if type(r) not in [int, float]:
        raise TypeError("The radius must be a non-negative real number")

    if r < 0:
        raise ValueError("Radius cannot be negative.")
    return pi*(r**2)
