import math
from tabulate import tabulate
from ...raw.ch7a import yield_point as yp

from dataclasses import dataclass

# @dataclass
# class YieldPoint:



# def yield_props(ρ1, ρ2, ρv, N, b, d, δtonos, fc, Ec, fy, Es, makelog=False, makelatex=False):
#     logtext = ''
#     latext = ''
#
#     α = Es/Ec
#     Asteel = ρ1 + ρ2 + ρv + N / (b * d * fy)
#     Bsteel = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos) + N / (b * d * fy)
#     ξysteel = ξycalc(α, Asteel, Bsteel, makelatex)
#     φysteel = fy / (Es * (1.0 - ξysteel[0]) * d)
#     Aconc = ρ1 + ρ2 + ρv - N / (1.8 * α * b * d * fc)
#     Bconc = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos)
#     ξyconc = ξycalc(α, Aconc, Bconc, makelatex)
#     φyconc = 1.8 * fc / (Ec * ξyconc[0] * d)
#
#     if φysteel<φyconc:
#         φy = φysteel
#         ξy = ξysteel[0]
#     else:
#         φy = φyconc
#         ξy = ξyconc[0]
#
#     if makelog:
#         headers = ['', 'value', 'units']
#         table = [['α', α],
#                  ['Asteel', Asteel],
#                  ['Bsteel', Bsteel],
#                  ['ξysteel', ξysteel[0], 'm'],
#                  ['φysteel', φysteel, 'm-1'],
#                  ['Aconc', Aconc],
#                  ['Bconc', Bconc],
#                  ['ξyconc', ξyconc[0]],
#                  ['φyconc', φyconc, 'm-1'],
#                  ['φy', φy, 'm-1'],
#                  ['ξy', ξy, 'm']]
#         logtext = tabulate(table, headers, tablefmt="pipe", floatfmt=".3E")
#
#
#     return α, Asteel, Bsteel, ξysteel[0], φysteel, Aconc, Bconc, ξyconc[0], φyconc, φy, ξy, logtext, latext