#Package created by Tinos Psomadakis
#Version 1.2
import os
import math
def version():
    print('''
Currently running tiquations Version 1.2
Changelog:

-NEW WEBSITE www.tiquations.com
-Added solar system index to planets (position of planets in solar system)
-Added eccentricity factor to planets
-Added volume to planets
-Added temperature conversion equations
-Huge bug fix
-More major bug fixes
-Added huge collection of elemnents from periodic table with help from python module periodictable
-Added docstrings
-Added important information to package (__author__, __copyright__ etc.)
''')

#Quadratic formula solver
def quadratic(num1,num2,num3):
    """Usage: (NUMx^2)=num1 (NUMx)=num2 (NUM)=num3 Example: 3x^2+5x-2 num1=3, num2=5, num3=-2"""
    last=math.sqrt(num2**2 - 4 * (num1) * (num3))
    result1 = -num2 + last
    ans1 = (result1 / (2 * num1))
    result2 = -num2 - last
    ans2 = (result2 / (2 * num1))
    return ans1, ans2

def pythagoras(a=None, b=None, c=None):
    """Given two sides of a triangle abc, solve for the missing side.

Usage: pythagoras(a=3,c=4) leaving out the side you want to solve for."""

    have_a, have_b, have_c = a is not None, b is not None, c is not None

    if not have_a and have_b and have_c:
        return math.sqrt((c**2)-(b**2))
    if have_a and not have_b and have_c:
        return math.sqrt((c**2)-(a**2))
    if have_a and have_b and not have_c:
       return math.sqrt((a**2)+(b**2))

    raise Exception("You must specify exactly two sides.")

'''
DEPRACATED
#Solve a using pythagoras
def pythagoras_a(b,c):
    return math.sqrt((c**2)-(b**2))


#Solve b using pythagoras
def pythagoras_b(a,c):
    return math.sqrt((c**2)-(a**2))


#Solve c using pythagoras
def pythagoras_c(a,b):
    return math.sqrt((a**2)+(b**2))

DEPRACATED
'''


#Solve distance using speed and time
def distance_dst(speed, time):
    """Usage: distance_dst(speed of object, time taken to get there)"""
    return speed*time

#Solve speed using distance and time
def speed_dst(distance, time):
    """Usage: speed_dst(distance traveled, time taken)"""
    return distance/time

#Solve time using speed and distance
def time_dst(distance, speed):
    """Usage: time_dst(distance traveled, speed of object)"""
    return distance/speed

#Solve force using mass and acceleration
def force_fma(mass,acceleration):
    """Usage: force_fma(mass of object, acceleration)"""
    return mass*acceleration


#Solve mass using force and acceleration
def mass_fma(force,acceleration):
    """Usage: mass_fma(force of object, acceleration of object)"""
    return force/acceleration


#Solve acceleration using mass and force
def acceleration_fma(force,mass):
    """Usage: acceleration_fma(force of object, mass of object)"""
    return force/mass


#Solve weight using mass and gravitational field strength
def weight_wmg(mass, gravitational_field_strength):
    """Usage: weight_wmg(Mass of object, gravitational field strength)"""
    return mass*gravitational_field_strength


#Solve mass using weight and gravitational field strength
def mass_wmg(weight, gravitational_field_strength):
    """Usage: mass_wmg(weight (Newtons), gravitational field strength)"""
    return weight/gravitational_field_strength


#Solve gravitational field strength using weight and mass
def gravity_wmg(weight, mass):
    """Usage: gravity_wmg(weight of object, mass of object)"""
    return weight/mass


#Solve for area of circle using radius
def circle_area_rad(radius):
    """Usage: Find circle's area from radius"""
    return math.pi*(radius**2)


#Solve for area of circle using diameter
def circle_area_dia(diameter):
    """Usage: Find circle's area from diameter"""
    return (1/4)*(math.pi*(diameter**2))


#Solve for diameter of circle using radius
def circle_diam_rad(radius):
    """Usage: Find circle's diameter from radius"""
    return radius*2


#Solve for diameter of circle using area
def circle_diam_are(area):
    """Usage: Find circle#s diameter from the area"""
    return 2*(math.sqrt(area/math.pi))


#Solve for circumference of circle using area
def circle_circum_rad(radius):
    """Usage: Find circumference from radius"""
    return 2*(math.pi*radius)


#Solve acceleration using Change in velocity and time
def acceleration_avt(delta_velocity,time):
    """Usage: acceleration_avt(change in speed, time taken)"""
    return delta_velocity/time


#Solve Change in velocity using acceleration and time
def delta_velocity_avt(acceleration,time):
    """Usage: delta_velocity_avt(acceleration of object, time taken)"""
    return acceleration*time


#Solve time taken using acceleration and change in velocity
def time_avt(acceleration,delta_velocity):
    """Usage: time_avt(acceleration of object, change in speed)"""
    return delta_velocity/acceleration


#Solve pressure using force and area
def pressure_fpa(force, area):
    """Usage: pressure_fpa(force of object, areaof object)"""
    return force/area


#Solve force using pressure and area
def force_fpa(pressure, area):
    """Usage: force_fpa(pressure, area of object)"""
    return pressure/area


#Solve area using pressure and force
def area_fpa(force, pressure):
    """Usage: area_fpa(force of object, pressure)"""
    return force*pressure


#Solve volume of a cylinder
def cylinder_vol(radius,height):
    """Usage: find volume of a cylinder"""
    return math.pi*(radius**2*(height))


#Solve surface area of a cylinder
def cylinder_surface_are(radius,height):
    """Usage: Find surface area of a cylinder"""
    return (2*(math.pi*radius*height))+2*(math.pi*(radius**2))


#Solve area of a trapezoid
def trapezoid_area(base_short,base_long,height):
    """Usage: Find the area of a trapezoid"""
    return ((base_short+base_long)/2)*height


#Solve height of a trapezoid
def trapezoid_height(base_short,base_long,area):
    """Usage: Find height of a trapezoid"""
    return 2*(area/(base_short+base_long))


#Solve surface area of a trapezoid
def trapezoid_surface_are(base_short,base_long,height):
    """Usage: Find the surface area of a trapezoid"""
    return ((base_short+base_long)/2)*height


def energy_evq(voltage,charge):
    """Usage: energy_evq(voltage, charge)"""
    return voltage*charge


def voltage_evq(energy,charge):
    """Usage: voltage_evq(energy, charge)"""
    return energy/charge


def charge_evq(energy,voltage):
    """Usage: charge_evq(energy,voltage)"""
    return energy/voltage


def power_piv(current, voltage):
    """Usage: power_piv(current, voltage)"""
    return current*voltage


def current_piv(power, voltage):
    """Usage: current_piv(power, voltage)"""
    return power/voltage


def voltage_piv(power, current):
    """Usage: voltage_piv(power,current)"""
    return power/current

def power_pet(energy,time):
    """Usage: power_pet(energy,time)"""
    return energy/time

def energy_pet(power,time):
    """Usage: energy_pet(power,time)"""
    return power*time

def time_pet(power,energy):
    """Usage: time_pet(power,energy)"""
    return energy/power

def sequence_nth(first_term,term_number,common_difference):
    """Usage: Find the nth term of a sequence"""
    return first_term+(common_difference*(term_number-1))

def sequence_first(nth,term_number,common_difference):
    """Usage: Find first number from a sequence"""
    return nth-(common_difference*(term_number-1))

def sequence_difference(nth,first_term,term_number):
    """Usage: Find the difference in a sequence"""
    return (nth-first_term)/(term_number-1)

def sequence_termnum(nth,first_term,common_difference):
    """Usage: Find the term number in a sequence"""
    return ((nth-first_term)/common_difference)+1

def orbitalspeed_vrt(radius,time):
    """Usage: orbitalspeed_vrt(radius of orbit, time taken)"""
    return (2*(math.pi)*radius)/time

def radius_vrt(orbitalspeed,time):
    """Usage: radius_vrt(orbit speed, time taken)"""
    return (orbitalspeed*time)/(2*math.pi)

def orbittime_vrt(orbitalspeed,radius):
    """Usage: orbittime_vrt(orbital speed, radius of orbit)"""
    return (2*math.pi*radius)/orbitalspeed

def cosine_side_a(b,c,angle_A):
    """Usage: Find side a"""
    return math.sqrt((b**2+c**2)-(2*(b*c*math.cos(angle_A))))

def cosine_side_b(a,c,angle_B):
    """Usage: Find side b"""
    return math.sqrt(a**2+c**2-(2*a*c*math.cos(angle_B)))

def cosine_side_c(a,b,angle_C):
    """Usage: Find side c"""
    return math.sqrt(a**2+b**2-(2*a*b*math.cos(angle_C)))

def cosine_angle_A(a,b,c):
    """Usage: Find angle A"""
    return math.acos(((b**2+c**2)-a**2)/(2*b*c))

def cosine_angle_B(a,b,c):
    """Usage: Find angle B"""
    return math.acos(((a**2+c**2)-b**2)/(2*a*c))

def cosine_angle_C(a,b,c):
    """Usage: Find angle C"""
    return math.acos(((a**2+b**2)-c**2)/(2*a*b))

def energy_emc(mass,speedoflight):
    """Usage: energy_emc(mass of object, speed of light) - You can use the constant light_speed."""
    return mass*speedoflight**2

def mass_emc(energy,speedoflight):
    """Usage: mass_emc(energy of an object, speed of light) - You can use the constant light_speed."""
    return energy/(speedoflight**2)

def speedoflight_emc(energy,mass):
    """Usage: Find the speed of light using energy and mass"""
    return math.sqrt(energy/mass)

def schwarzschild(gravity,mass,speedoflight):
    """Usage: schwarzschild(gravity, mass, speed of light) - Note: you can use the constant earth_g for the earth's gravity and light_speed for the speed of light."""
    return (2*gravity*mass)/(speedoflight**2)

def sphere_mass(density,radius):
    """Usage: Find the mass of a sphere using density and radius"""
    return density*((4/3)*(math.pi)*radius**3)

def sphere_density(mass,radius):
    """Usage: Find the density of a sphere using mass and radius"""
    return mass/((4/3)*math.pi*radius**3)

def sphere_radius(mass,density):
    """Usage: Find the radius of a sphere knowing mass and density"""
    return (mass/(density*(4/3)*math.pi))** (1. / 3)

def cube_vol(side_length):
    """Usage: cube_volume(Side of one length)"""
    return side_length**3

def rectangle_vol(length,width,height):
    """Usage: rectangle_vol(length rectangle, width of rectangle, height of rectangle)"""
    return length*width*height

def sphere_vol(radius):
    """Usage: Find the volume of a sphere using the radius"""
    return (4*math.pi*(radius**3))/3

def cone_vol(radius,height):
    """Usage: Find the volume of a cone using radius and height"""
    return (math.pi*(radius**2)*height)/3

def pyramid_vol(base_area,height):
    """Usage: Find the volume of a pyramid  using base area and height"""
    return (base_area*height)/3

#GitHub SirEraz

def force_fmg(mass,gravitational_field_strength):
    """Usage: Find force of gravity using mass and a gravitational constant """
    return mass * gravitational_field_strength
#(f(g)=mg) find mass using force of grav and g
def mass_fmg(force,gravitational_field_strength):
    """Usage: Find mass using force of gravity and a gravitational constant """
    return force / gravitational_field_strength
#(f(g)=mg) find grav constant using force of g and mass
def gravity_fmg(force,mass):
    """Usage: Find gravity using force and mass """
    return force / mass

def friction_fnc(normal_force,friction_coefficient):
    """Usage: Find force of friction using normal force and friction coefficent"""
    return normal_force * friction_coefficient
#(F(f)=u*F(n)) finds normal force (F(n)) using F(f) and friction coefficient (u)
def normal_fnc(friction_force,friction_coefficient):
    """Usage: Find normal force using force of friction and friction coefficent"""
    return friction_force / friction_coefficient
#(F(f)=u*F(n)) finds friction coefficient (u) using F(f) and F(n)
def coefficient_fmc(friction_force,normal_force):
    """Usage: Find friction coefficent using force of friction and normal force"""
    return friction_force / normal_force

def acceleration_aug(friction_coefficient,gravity):
    """Usage: Find acceleration using friction coefficient and gravitational constant"""
    return friction_coefficient * gravity
#(a=ug) find fric. coefficient (u) using acceleration and grav constant
def coefficient_aug(acceleration,gravity):
    """Usage: Find friction coefficient using acceleration and gravitational constant"""
    return acceleration / gravity
#(a=ug) find grav constant using u and a
def gravity_aug(acceleration,friction_coefficient):
    """Usage: Find gravitational constant using acceleration and friction coefficient"""
    return acceleration / friction_coefficient

def coefficient_cfn(friction,normal):
    """Usage: Find coefficient with friction and normal force"""
    return friction / normal
#(u=F(f)/F(n)) find F(f) with u and F(n)
def friction_cfn(coefficient,normal):
    """Usage: Find friction using coefficient and normal force"""
    return coefficient * normal
#(u=F(f)/F(n)) find F(n) with u and F(f)
def normal_cfn(coefficient,friction):
    """Usage: Find normal force using coefficient and friction"""
    return friction / coefficient

def radius_rf(focal_point):
    """Usage: radius with focal point for concave and convex mirrors"""
    return 2 *focal_point
#(C=2f) find focal point with C
def focal_rf(radius):
    """Usage: focal point with radius for concave and convex mirrors"""
    return radius / 2

#(f=(di*do/di+do)) find focal point (f) with d(i) and d(o)
def focal_point(distance_image,distance_object):
    """Usage: Find focal point with distance of image and distance of object"""
    numerator = distance_image * distance_object
    denominator = distance_image + distance_object
    return numerator / denominator
#d(i)=(f*do/do-f) find d(i) with focal point and d(o)
def mirror_distance_image(focal_point,distance_object):
    """Usage: Find distance of image with focal point and distance of object"""
    numerator = focal_point * distance_object
    denominator = distance_object - focal_point
    return numerator / denominator
#d(o)=(f*di/di-f) find d(o) with focal point and d(i)
def mirror_distance_object(focal_point,distance_image):
    """Usage: Find distance of object with focal point and distance of image"""
    numerator = focal_point * distance_image
    denominator = distance_image - focal_point
    return numerator / denominator

#the following equations are variations of m=(hi/ho)=(-di/do)
#find m with h(i) and h(o)
def mirror_mag_h(height_image,height_object):
    """Usage: Find magnification using height of image and height of object"""
    return height_image/ height_object
#find m with d(i) and d(o)
def mirror_mag_d(distance_image,distance_object):
    """Usage: Find magnification using distance of image and distance of object"""
    neg_di = (-1) * distance_image
    return neg_di / distance_object
#find h(i) with m and h(o)
def mirror_hi_m(magnification,height_object):
    """Usage: Find height of image using magnification and height of object"""
    return magnification * height_object
#find h(i) with d(i), d(o), and h(o)
def mirror_hi_hodido(distance_image,distance_object,height_object):
    """Usage: Find height of image using height of object, distance of object and height of object"""
    neg_di = (-1) * distance_image
    numerator = neg_di * height_object
    return numerator / distance_object
#find h(o) with m and h(i)
def mirror_ho_m(height_image,magnification):
    """Usage: Find height of object using magnification"""
    return height_image / magnification
#find h(o) with d(i), d(o), h(i)
def mirror_ho_hidido(distance_image,distance_object,height_image):
    """Usage: Find height of object using height of image, distance of object and height of object"""
    neg_di = (-1) * distance_image
    numerator = height_image * distance_object
    return numerator / neg_di

#PENDULUMS
#T = period
#L = length of string (of pendulum)
#g = grav constant (acceleration of grav)

#T = 2(math.pi)*sqrt(L/g)

#find T with L and g
def time_tlg(length,gravity):
    """Usage: PENDULUMS - Find time using length and gravity"""
    return (2 * math.pi) *(math.sqrt(length / gravity))
#find L with T and g
def length_tlg(time,gravity):
    """Usage: PENDULUMS - Find length using time and gravity"""
    return gravity * (time / (2 * math.pi))**2
#find g with T and L
def gravity_tlg(time,length):
    """Usage: PENDULUMS - Find gravity using time and length"""
    return (2 * math.pi)**2 / time**2

#END OF SIR ERAZ GITHUB

def wave_frequency_t(time_period):
    """Usage: Finding the wave frequency using time period.
    f=1/T"""
    return 1/time_period

def wave_speed_flv(frequency,wave_length):
    """Usage: Finding the wave speed using frequency and wave length.
    v=f×λ"""
    return frequency*wave_length

def frequency_flv(wave_length,wave_speed):
    """Usage: Finding the frequency using wave speed and wave length.
    f=v/λ"""
    return wave_speed/wave_length

def wave_length_flv(frequency,wave_speed):
    """Usage: Finding the wave length using frequency and wave speed.
    λ=v/f"""
    return wave_speed/frequency

def refractive_index_nir(angle_incidence,angle_refraction):
    """Usage: Find refractive index using angle of incidence and angle of refraction"""
    refractive_index_nir_resul=math.sin(angle_incidence)/math.sin(angle_refraction)
    return refractive_index_nir_resul

def angle_incidence_nir(refractive_index,angle_refraction):
    """Usage: Find angle of incidence using refractive index and angle of refraction
    returns in radians"""
    angle_incidence_nir_resul=refractive_index*math.sin(angle_refraction)
    return angle_incidence_nir_resul

def angle_refraction_nir(refractive_index,angle_incidence):
    """Usage: Find angle of refraction using refractive index and angle of incidence
    returns in radians"""
    angle_refraction_nir_resul=math.sin(angle_incidence)/refractive_index
    return angle_refraction_nir_resul

def Kelvin_C(Celsius):
    """Usage: Convert to Kelvin from Celsius
    Kelvin_C(Celsius)"""
    return Celsius+273.15

def Kelvin_F(Fahrenheit):
    """Usage: Convert to Kelvin from Fahrenheit
    Kelvin_F(Fahrenheit)"""
    return  (Fahrenheit-32) * 5/9 + 273.15

def Celsius_K(Kelvin):
    """Usage: Convert to Celsius from Kelvin
    Celsius_K(Kelvin)"""
    return Kelvin-273.15

def Celsius_F(Fahrenheit):
    """Usage: Convert to Celsius from Fahrenheit
    Celsius_F(Fahrenheit)"""
    return  (Fahrenheit-32)*5/9

def Fahrenheit_C(Celsius):
    """Usage: Convert to Fahrenheit from Celsius
    Fahrenheit_C(Celsius)"""
    return (Celsius* 9/5)+32

def Fahrenheit_K(Kelvin):
    """Usage: Convert to Fahrenheit from Kelvin
    Fahrenheit_K(Kelvin)"""
    return (Kelvin-273.15)*9/5 + 32

def kinetic_energy_kmv(mass,velocity):
    """Usage: Find kinetic energy from mass and velocity"""
    result = 0.5*(mass*velocity**2)
    return result

def mass_kmv(kinetic_energy,velocity):
    """Usage: Find mass from kinetic energy and velocity"""
    result = (2*kinetic_energy)/velocity**2
    return result

def velocity_kmv(kinetic_energy,mass):
    """Usage: Find velocity from kinetic energy and mass"""
    result = math.sqrt(kinetic_energy/(0.5*mass))
    return result

def GPE_gpemgh(mass,gravity,height):
    """Usage: Find gravitational potential energy from mass, gravity and height"""
    result=mass*gravity*height
    return result

def mass_gpemgh(GPE,gravity,height):
    """Usage: Find mass from gravitational potential energy, gravity and height"""
    result=GPE/gravity*height
    return result

def gravity_gpemgh(GPE,mass,height):
    """Usage: Find gravity from gravitational potential energy, mass and height"""
    result=GPE/mass*height
    return result

def height_gpemgh(GPE,mass,gravity):
    """Usage: Find height from gravitational potential energy, mass and gravity"""
    result=GPE/mass*gravity
    return result


def help():
    #General
    print('''
https://www.tiquations.com

A python package containing useful equations for science and maths.
Created by Tinos Psomadakis\n
          ''')
    #Commands
    print("Angles are always measured in radians")
    print('''
Commands:

quadratic(a,b,c) - Find quadratic formula from an equation like 3x^2+6x+2 = 0 where a=3, b=6 and c=2.
distance_dst(speed,time) - Find distance using speed and time
speed_dst(distance,time) - Find speed using distance and time
time_dst(distance,speed) - Find time using distance and speed
force_fma(mass,acceleration) - Find force using mass and acceleration
mass_fma(force,acceleration) - Find mass using force and acceleration
acceleration_fma(force,mass) - Find acceleration using force and mass
force_fmg(mass,gravitational_field_strength) - Find force using the mass and gravitational field strength
mass_fmg(force,gravitational_field_strength) - Find mass using the force and gravitational field strength
gravity_fmg(force,mass) - Find gravitational field strength using force and mass
weight_wmg(mass, gravitational_field_strength) - Find weight using mass and gravitational field strength
mass_wmg(weight, gravitational_field_strength) - Find mass using weight and gravitational field strength
gravity_wmg(weight, mass) - Find gravitational field strength using weight and mass
circle_area_rad(radius) - Find area of a circle using radius
circle_area_dia(diameter) - Find area of a circle using diameter
circle_diam_rad(radius) - Find diameter of a circle using radius
circle_diam_are(area) - Find diameter of a circle using area
circle_circum_rad(radius) - Find circumference of a circle
acceleration_avt(delta_velocity,time) - Find acceleration using change in velocity and time
delta_velocity_avt(acceleration,time) - Find change in velocity using acceleration and time
time_avt(acceleration,delta_velocity) - Find time taken using change in velocity and acceleration
pressure_fpa(force, area) - Find pressure using force and area
force_fpa(pressure, area) - Find force using pressure and area
area_fpa(force, pressure) - Find area using force and pressure
cylinder_vol(radius,height) - Find volume of cylinder
cylinder_surface_are(radius,height) - Find surface area of cylinder
trapezoid_area(base_short,base_long,height) - Find area of trapezoid
trapezoid_height(base_short,base_long,area) - Find height of trapezoid
trapezoid_surface_are(base_short,base_long,height) - Find surface are of trapezoid
pythagoras(a=None, b=None, c=None) - Use pythagoras' theorum to solve for a missing side
energy_evq(voltage,charge) - Find energy using potential difference and charge
voltage_evq(energy,charge) - Find potential difference using energy and charge
charge_evq(energy,voltage) - Find charge using energy and potential difference
power_piv(current, potential_difference) - Find power using current and potential difference
current_piv(power, potential_difference) - Find current using power and potential difference
potential_dif_piv(power, current) - Find potential difference using power and current
power_pet(energy,time) - Find power using energy and time
energy_pet(power,time) - Find energy using power and time
time_pet(power,energy) - Find time using power and energy
sequence_nth(first_term,term_number,common_difference) - Find nth term of sequence
sequence_first(nth,term_number,common_difference) - Find the first term of a sequence
sequence_difference(nth,first_term,term_number) - Find difference of a sequence
sequence_termnum(nth,first_term,common_difference) - Find term number of a sequence
orbitalspeed_vrt(radius,time) - Find orbital speed using radius and orbit time
radius_vrt(orbitalspeed,time) - Find radius using orbital speed and orbit time
orbittime_vrt(orbitalspeed,radius) - Find orbit time using orbital speed and radius
cosine_side_a(b,c,A_radians) - Find side a using cosine rule
cosine_side_b(a,c,B_radians) - Find side b using cosine rule
cosine_side_c(a,b,C_radians) - Find side c using cosine rule
cosine_angle_A(a,b,c) - Find angle A using cosine rule
cosine_angle_B(a,b,c) - Find angle B using cosine rule
cosine_angle_C(a,b,c) - Find angle C using cosine rule
energy_emc(mass,speedoflight) - Find energy using mass and speed of light
mass_emc(energy,speedoflight) - Find mass using energy and speed of light
speedoflight_emc(energy,mass) - Find speed of light using energy and mass. You can also use the light_speed constant.
schwarzschild(gravity,mass,speedoflight) - Find the Schwarzschild radius of a black hole
sphere_mass(density,radius) - Find mass of a sphere using density and radius
sphere_density(mass,radius) - Find density of a sphere using mass and radius
sphere_radius(mass,density) - Find radius of a sphere using mass and density
cube_vol(side_length) - Find the volume of a cube using one side
rectangle_vol(length,width,height) - Find the volume of a rectangle using length, width and height
sphere_vol(radius) - Find the volume of a sphere using it's radius
cone_vol(radius,height) - Find the volume of a cone using the radius and height
pyramid_vol(base_area,height) - Find the volume of a pyramid using the area of the base and height#


NEW IN TIQUATIONS 1.2

wave_frequency_t(time_period) - Find wave frequency using time
wave_speed_flv(frequency,wave_length) - Find wave speed using frequency and wave speed
frequency_flv(wave_length,wave_speed) - Find frequency using wave length and wave speed
wave_length_flv(frequency,wave_speed)  - Find wave length using frequency and wave speed
refractive_index_nir(angle_incidence,angle_refraction) - Find refractive index using angle of incidence and angle of refraction
angle_incidence_nir(refractive_index,angle_refraction) - Find angle of incidence using refractive index and angle of angle_refraction
angle_refraction_nir(refractive_index,angle_incidence) - Find angle of refraction using refractive index and angle of incidence
Kelvin_C(Celsius) - Convert Celsius to Kelvin
Kelvin_F(Fahrenheit) - Convert Fahrenheit to Kelvin
Celsius_K(Kelvin) - Convert Kelvin to Celsius
Celsius_F(Fahrenheit) - Convert Fahrenheit to Celsius
Fahrenheit_C(Celsius) - Convert Celsius to Fahrenheit
Fahrenheit_K(Kelvin) - Convert Kelvin to Fahrenheit
kinetic_energy_kmv(mass,velocity) - Find kinetic energy using mass and velocity
velocity_kmv(kinetic_energy,mass) - Find velocity using kinetic energy and mass
mass_kmv(kinetic_energy,velocity) - Find mass using kinetic energy and velocity
GPE_gpemgh(mass,gravity,height) - Find gravitational potential energy using mass, gravity and height
mass_gpemgh(GPE,gravity,height) - Find mass using gravitational potential energy, gravity and height
gravity_gpemgh(GPE,mass,height) - Find gravity using gravitational potential energy, mass and height
height_gpemgh(GPE,mass,gravity) - Find height using gravitational potential energy, mass and gravity
friction_fnc(normal_force,friction_coefficient) - Find force of friction using normal force and friction coefficent
normal_fnc(friction_force,friction_coefficient) - Find normal force using force of friction and friction coefficent
coefficient_fmc(friction_force,normal_force) - Find friction coefficent using force of friction and normal force
acceleration_aug(friction_coefficient,gravity) - Find acceleration using friction coefficient and gravitational constant
coefficient_aug(acceleration,gravity) - Find friction coefficient using acceleration and gravitational constant
gravity_aug(acceleration,friction_coefficient) - Find gravitational constant using acceleration and friction coefficient
coefficient_cfn(friction,normal) - Find coefficient with friction and normal force
friction_cfn(coefficient,normal) - Find friction using coefficient and normal force
normal_cfn(coefficient,friction) - Find normal force using coefficient and friction
radius_rf(focal_point) -radius with focal point for concave and convex mirrors
focal_rf(radius) - focal point with radius for concave and convex mirrors
focal_point(distance_image,distance_object) - Find focal point with distance of image and distance of object
mirror_distance_image(focal_point,distance_object) - Find distance of image with focal point and distance of object
mirror_distance_object(focal_point,distance_image) - Find distance of object with focal point and distance of image
mirror_mag_h(height_image,height_object) - Find magnification using height of image and height of object
mirror_mag_d(distance_image,distance_object) - Find magnification using distance of image and distance of object
mirror_hi_m(magnification,height_object) - Find height of image using magnification and height of object
mirror_hi_hodido(distance_image,distance_object,height_object) - Usage: Find height of image using height of object, distance of object and height of object
mirror_ho_m(height_image,magnification) - Find height of object using magnification
mirror_ho_hidido(distance_image,distance_object,height_image) - Find height of object using height of image, distance of object and height of object
time_tlg(length,gravity) - PENDULUMS: Find time using length and gravity
length_tlg(time,gravity) - PENDULUMS: Find length using time and gravity
gravity_tlg(time,length) - PENDULUMS: Find gravity using time and length

Usage:
hello = tiquations.example_xyz(5,72)
testing = tiquations.quadratic(1,2,-3)

          ''')

    #Built-in variables
    print('''
Built-in constants:
earth.gravity = 9.807 m/s^2
moon.gravity = 1.62 m/s^2
mars.gravity = 3.711 m/s^2
jupiter.gravity = 24.79 m/s^2
neptune.gravity = 11.15 m/s^2
mercury.gravity = 3.7 m/s^2
saturn.gravity = 10.44 m/s^2
uranus.gravity = 8.87 m/s^2
venus.gravity = 8.87 m/s^2
pluto.gravity = 0.62 m/s^2

earth.mass =  5.98 * 10^24 kg
earth.radius = 6371 km
earth.surface_area = 510.1 km^2

moon.mass = 7.34767309e22 kg
moon.radius = 1737.1 km
moon.surface_area = 3.793e7 km^2

mars.mass = 6.4171e23 kg
mars.radius = 3389.5 km
mars.surface_area = 114.8 km^2

jupiter.mass = 1.898e27 kg
jupiter.radius = 69911 km
jupiter.surface_area = 61420 km^2

neptune.mass = 1.024e26 kg
neptune.radius = 24622 km
neptune.surface_area = 7618 km^2

mercury.mass = 3.285e23 kg
mercury.radius = 2439.7 km
mercury.surface_area = 74.8 km^2

saturn.mass = 5.683e26 kg
saturn.radius = 58232 km
saturn.surface_area = 42700 km^2

uranus.mass = 8.681e25 kg
uranus.radius = 25362 km
uranus.surface_area = 8083 km^2

venus.mass = 4.867e24 kg
venus.radius = 6051.8 km
venus.surface_area = 460.2 km^2

pluto.mass = 1.30900e22 kg
pluto.radius = 1188.3 km
pluto.surface_area = 16647940 km^2

earth.sun_distance = 149,597,870 km
mars.sun_distance = 227,940,000 km
mercury.sun_distance = 57,900,000 km
venus.sun_distance = 108,200,000 km
jupiter.sun_distance = 778,300,000 km
neptune.sun_distance = 4,497,100,000 km
saturn.sun_distance = 1,427,000,000 km
uranus.sun_distance = 2,871,000,000 km
pluto.sun_distance = 5,913,000,000 km

speed_of_light = 299792458 m/s
pi = 3.141592653589793
eulersnum = 2.7182818284590452353602874713527
eulersmasch = 0.577215664901532860606512
golden_ratio = 1.6180339887498948420
light_speed = 299792458 m/s
boltzmann = 1.380649e−23 J/K
gas_constant = 8.314462618 J/mol K
luminous_efficacy = 683 lm/W
atmosphere = 101325 Pa
avogadros_num = 6.02214086 * 10^23 mol^-1


mass in KG
radius in KM
surface area in km^2
gravity in m/s^2

Usage:
var = tiquations.example(pi,67)
weight = tiquations.weight_wmg(52, earth_g)

Type tiquations.variables() to see a full list with attached values
        ''')
