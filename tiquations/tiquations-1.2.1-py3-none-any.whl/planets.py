#!/usr/bin/env python
class Planets(object):
    """Information about the planets in the solar system

    Features:
    index - Integer
    gravity - Float
    mass - Float
    radius - Float
    surface_area - Float
    sun_distance - Integer
    eccentricity - Float
    volume - Float

    Example: saturn.surface_area
    """
    def __init__(self,index,gravity,mass,radius,surface_area,sun_distance,eccentricity,volume):
        self.gravity=gravity
        self.mass=mass
        self.radius=radius
        self.surface_area=surface_area
        self.sun_distance=sun_distance
        self.eccentricity=eccentricity
        self.volume=volume

earth=Planets(2,9.807,5.972e24,6371,510.1,149597870,0.0167086,1.08321e21)
moon=Planets(2,1.62,7.34767309e22,1737.1,3.793e7,152503397,0.0549,2.1958e10)
mars=Planets(3,3.711,6.4171e23,3389.5,114.8,227940000,0.0934,1.6318e11)
jupiter=Planets(4,24.79,1.898e27,69911,61420,778300000,0.0489,1.4313e15)
neptune=Planets(7,11.15,1.024e26,24622,7618,4497100000,0.009456,6.254e13)
mercury=Planets(0,3.7,3.285e23,2439.7,74.8,57900000,0.205630,6.083e10)
saturn=Planets(5,10.44,5.683e26,58232,42700,1427000000,0.0565,8.2713e14)
uranus=Planets(6,8.87,8.681e25,25362,8083,2871000000,0.046381,6.833e13)
venus=Planets(1,8.87,4.867e24,6051.8,460.2,108200000,0.006772,9.2843e11)
pluto=Planets(8,0.61,1.30900e22,1188.3,16647940,5913000000,0.24880766,7.057e9)
