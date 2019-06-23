import math
import numpy as np
import matplotlib.pyplot as plt
from sympy.solvers import solve
from sympy import Symbol


fwc = 1.5       # MPa
l = 6.0         # m
h = 3.0         # m
t = 0.2         # m
ρ = 1           # %

kw = 1.71 * fwc * (80 + h / t)
γcr = 0.09 / (math.pow(fwc, 0.5) * (80 + h / t))
τcr = kw * γcr

τu = 0.22 * math.pow(fwc, 0.5)
γu = 4.545 * γcr

print('kw = {0:.2f}MPa'.format(kw))
print('γcr = {0:.6f}'.format(γcr))
print('τcr = {0:.4f}MPa'.format(τcr))

print('γu = {0:.6f}'.format(γu))
print('τu = {0:.4f}MPa'.format(τu))

def τ(γ: float, τu: float, γu: float, ρ: float):
    x1 = (γ / γu) -1
    x2 = np.power(ρ, 3.82)
    return τu * (1 - 0.24 * np.sqrt( x1 / x2))

τ002 = τ(0.02, τu, γu, ρ)
print('τ0.02 = {0:.6f}'.format(τ002))

x1 = [0, γcr, γu]
y1 = [0, τcr, τu]

x2 = np.linspace(γu, 0.02, 50)
y2 = τ(x2, τu, γu, ρ)

Area = np.trapz(y2, x2)
print('Area = {0:.6f}'.format(Area))


γtmp = Symbol('γtmp')


γD = solve((τ002 * (0.02 - γtmp) + 0.5 * (γtmp - γu) * (τ002 + τu) - Area), γtmp)[0]
print('γD = {0:.6f}'.format(γD))

# τ002 * (0.02 - γD) + 0.5 * (γD - γu) * (τ002 + τu)


# υ = Symbol('υ')
# μθV=solve((((h-x)/(2*Ls))*min(N/1000, 0.55*b*d*fc/1000) + (1-0.05*υ) * (0.16*max(0.5, 100*ρtot)*(1-0.16*min(5,αs))*math.pow(fc/1000, 0.5)*b*d + Vw/1000)*1000-My/Ls),υ)[0]
#
# print(μθV)

xlin = [0, γcr, γu, γD, 0.02]
ylin = [0, τcr, τu, τ002, τ002]


plt.plot(x1, y1, lw=2)
plt.plot(x2, y2, lw=2)
plt.plot(xlin, ylin, lw=2)
#plt.axis([0, 1.2 * 100 * γu, 0, 1.2 * τu])
plt.axis([0, 0.021, 0, 1.1 * τu])
plt.ylabel('τ (MPa)')
plt.xlabel('γ')
plt.title('τ vs γ')

# plt.savefig( 'myfig.png' )
# plt.show()


kw_BC = (τu - τcr) / (γu - γcr)
kw_CD = (τ002 - τu) / (γD - γu)

print('kw_BC = {0:.2f}'.format(kw_BC))
print('kw_CD = {0:.2f}'.format(kw_CD))

Aw = l * t
α = np.arctan(h/l)  # Η γωνία με την οριζόντιο

EsAs_AB = 1000 * Aw * kw / (math.sin(α) * math.cos(α) * math.cos(α))
EsAs_BC = 1000 * Aw * kw_BC / (math.sin(α) * math.cos(α) * math.cos(α))
EsAs_CD = 1000 * Aw * kw_CD / (math.sin(α) * math.cos(α) * math.cos(α))

print('AsAs_AB = {0:.2f}'.format(EsAs_AB))
print('AsAs_BC = {0:.2f}'.format(EsAs_BC))
print('AsAs_CD = {0:.2f}'.format(EsAs_CD))

d = math.sqrt(math.pow(h,2) + math.pow(l,2))
dA = d
dB = math.sqrt(math.pow(h,2) + math.pow(l - h * γcr, 2))
dC = math.sqrt(math.pow(h,2) + math.pow(l - h * γu, 2))
dD = math.sqrt(math.pow(h,2) + math.pow(l - h * γD, 2))
dE = math.sqrt(math.pow(h,2) + math.pow(l - h * 0.02, 2))

print('dA = {0:.4f}'.format(dA))
print('dB = {0:.4f}'.format(dB))
print('dC = {0:.4f}'.format(dC))
print('dD = {0:.4f}'.format(dD))
print('dE = {0:.4f}'.format(dE))

δA = 0.0
δB = - (dB - dA)
δC = - (dC - dA)
δD = - (dD - dA)
δE = - (dE - dA)

print('δA = {0:.4f}'.format(δA))
print('δB = {0:.4f}'.format(δB))
print('δC = {0:.4f}'.format(δC))
print('δD = {0:.4f}'.format(δD))
print('δE = {0:.4f}'.format(δE))

FA = 0
FB = EsAs_AB * δB / d
FC = EsAs_BC * (δC - δB) / d + FB
FD = EsAs_CD * (δD - δC) / d + FC
FE = FD

print('FA = {0:.4f}'.format(FA))
print('FB = {0:.4f}'.format(FB))
print('FC = {0:.4f}'.format(FC))
print('FD = {0:.4f}'.format(FD))
print('FE = {0:.4f}'.format(FE))

XFδ = [δA, δB, δC, δD, δE]
YFδ = [FA, FB, FC, FD, FE]

plt.plot(XFδ, YFδ, lw=2)
plt.axis([0, 1.1 * δE, 0, 1.1 * FC])
plt.ylabel('F (kN)')
plt.xlabel('δ (m)')
plt.title('F vs δ')

plt.show()