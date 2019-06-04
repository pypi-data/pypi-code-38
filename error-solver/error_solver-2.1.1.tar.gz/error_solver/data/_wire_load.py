"""
Created by Error Solver on 2019-04-14 22:39:06

0: wind_pressure - wind_pressure_coeff*wind_velocity**2
1: horz_unit_load - wind_pressure*(diameter + 2*ice_thickness)*sin(azimuth - wind_azimuth)**2
2: -pi*ice_density*ice_thickness*(diameter + ice_thickness) - unit_weight + vert_unit_load
3: -horz_unit_load**2 - vert_unit_load**2 + (-k_factor + unit_load)**2
"""

from math import *


# Equation 0
def eq0(wind_velocity, wind_pressure_coeff, wind_pressure, **kwargs):
    return wind_pressure - wind_pressure_coeff*wind_velocity**2


def eq0_wind_velocity(wind_velocity, wind_pressure_coeff, wind_pressure, **kwargs):
    return -2*wind_pressure_coeff*wind_velocity


def eq0_wind_pressure_coeff(wind_velocity, wind_pressure_coeff, wind_pressure, **kwargs):
    return -wind_velocity**2


def eq0_wind_pressure(wind_velocity, wind_pressure_coeff, wind_pressure, **kwargs):
    return 1


# Equation 1
def eq1(horz_unit_load, azimuth, ice_thickness, diameter, wind_azimuth, wind_pressure, **kwargs):
    return horz_unit_load - wind_pressure*(diameter + 2*ice_thickness)*sin(azimuth - wind_azimuth)**2


def eq1_horz_unit_load(horz_unit_load, azimuth, ice_thickness, diameter, wind_azimuth, wind_pressure, **kwargs):
    return 1


def eq1_azimuth(horz_unit_load, azimuth, ice_thickness, diameter, wind_azimuth, wind_pressure, **kwargs):
    return -2*wind_pressure*(diameter + 2*ice_thickness)*sin(azimuth - wind_azimuth)*cos(azimuth - wind_azimuth)


def eq1_ice_thickness(horz_unit_load, azimuth, ice_thickness, diameter, wind_azimuth, wind_pressure, **kwargs):
    return -2*wind_pressure*sin(azimuth - wind_azimuth)**2


def eq1_diameter(horz_unit_load, azimuth, ice_thickness, diameter, wind_azimuth, wind_pressure, **kwargs):
    return -wind_pressure*sin(azimuth - wind_azimuth)**2


def eq1_wind_azimuth(horz_unit_load, azimuth, ice_thickness, diameter, wind_azimuth, wind_pressure, **kwargs):
    return 2*wind_pressure*(diameter + 2*ice_thickness)*sin(azimuth - wind_azimuth)*cos(azimuth - wind_azimuth)


def eq1_wind_pressure(horz_unit_load, azimuth, ice_thickness, diameter, wind_azimuth, wind_pressure, **kwargs):
    return -(diameter + 2*ice_thickness)*sin(azimuth - wind_azimuth)**2


# Equation 2
def eq2(unit_weight, vert_unit_load, diameter, ice_thickness, ice_density, **kwargs):
    return -pi*ice_density*ice_thickness*(diameter + ice_thickness) - unit_weight + vert_unit_load


def eq2_unit_weight(unit_weight, vert_unit_load, diameter, ice_thickness, ice_density, **kwargs):
    return -1


def eq2_vert_unit_load(unit_weight, vert_unit_load, diameter, ice_thickness, ice_density, **kwargs):
    return 1


def eq2_diameter(unit_weight, vert_unit_load, diameter, ice_thickness, ice_density, **kwargs):
    return -pi*ice_density*ice_thickness


def eq2_ice_thickness(unit_weight, vert_unit_load, diameter, ice_thickness, ice_density, **kwargs):
    return -pi*ice_density*ice_thickness - pi*ice_density*(diameter + ice_thickness)


def eq2_ice_density(unit_weight, vert_unit_load, diameter, ice_thickness, ice_density, **kwargs):
    return -pi*ice_thickness*(diameter + ice_thickness)


# Equation 3
def eq3(horz_unit_load, unit_load, vert_unit_load, k_factor, **kwargs):
    return -horz_unit_load**2 - vert_unit_load**2 + (-k_factor + unit_load)**2


def eq3_horz_unit_load(horz_unit_load, unit_load, vert_unit_load, k_factor, **kwargs):
    return -2*horz_unit_load


def eq3_unit_load(horz_unit_load, unit_load, vert_unit_load, k_factor, **kwargs):
    return -2*k_factor + 2*unit_load


def eq3_vert_unit_load(horz_unit_load, unit_load, vert_unit_load, k_factor, **kwargs):
    return -2*vert_unit_load


def eq3_k_factor(horz_unit_load, unit_load, vert_unit_load, k_factor, **kwargs):
    return 2*k_factor - 2*unit_load


# Assembled functions
EQUATIONS = [
    eq0,
    eq1,
    eq2,
    eq3
]


PARTIALS = [
    {'wind_velocity': eq0_wind_velocity, 'wind_pressure_coeff': eq0_wind_pressure_coeff, 'wind_pressure': eq0_wind_pressure},
    {'horz_unit_load': eq1_horz_unit_load, 'azimuth': eq1_azimuth, 'ice_thickness': eq1_ice_thickness, 'diameter': eq1_diameter, 'wind_azimuth': eq1_wind_azimuth, 'wind_pressure': eq1_wind_pressure},
    {'unit_weight': eq2_unit_weight, 'vert_unit_load': eq2_vert_unit_load, 'diameter': eq2_diameter, 'ice_thickness': eq2_ice_thickness, 'ice_density': eq2_ice_density},
    {'horz_unit_load': eq3_horz_unit_load, 'unit_load': eq3_unit_load, 'vert_unit_load': eq3_vert_unit_load, 'k_factor': eq3_k_factor}
]


COMBOS = {
    'wind_velocity': [0, 1, 2, 3],
    'wind_pressure': [1, 2, 3]
}
