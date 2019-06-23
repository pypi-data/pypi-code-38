import math
from tabulate import tabulate

def ξycalc(α, A, B, makelatex=False):
    """
        Το ύψος της θλιβόµενης ζώνης στη διαρροή, ξy, ανηγµένο στο στατικό ύψος d, είναι:

        .. math::
            ξ_y=(α^2A^2+2αB)^{0.5}-αA

    Args:
        α (float): Ο λόγος των μέτρων ελαστικότητας :math:`α = E_s/E_c`
        A (float): Ο συντελεστής A που υπολογίζονται για διαρροή λόγω χάλυβα ή μη-γραμμικότητα σκυροδέματος
        B (float): Ο συντελεστής B που υπολογίζονται για διαρροή λόγω χάλυβα ή μη-γραμμικότητα σκυροδέματος
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]
    """
    value = math.pow((math.pow(α, 2) * math.pow(A, 2) + 2 * α * B), 0.5) - α * A
    if makelatex:
        text = r"ξ_y=(α^2A^2+2αB)^{0.5}-αA" \
               + f'=({α:.3f}^2\cdot {A:.5f}^2+2\cdot {α:.3f}\cdot {B:.5f})^{{0.5}}-{α:.3f}\cdot {A:.5f}={value:.4f}'
    else:
        text = ''

    return value, text


def yield_props(ρ1, ρ2, ρv, N, b, d, δtonos, fc, Ec, fy, Es, makelog=False, makelatex=False):
    logtext = ''
    latext = ''

    α = Es/Ec
    Asteel = ρ1 + ρ2 + ρv + N / (b * d * fy)
    Bsteel = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos) + N / (b * d * fy)
    ξysteel = ξycalc(α, Asteel, Bsteel, makelatex)
    φysteel = fy / (Es * (1.0 - ξysteel[0]) * d)
    Aconc = ρ1 + ρ2 + ρv - N / (1.8 * α * b * d * fc)
    Bconc = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos)
    ξyconc = ξycalc(α, Aconc, Bconc, makelatex)
    φyconc = 1.8 * fc / (Ec * ξyconc[0] * d)

    if φysteel<φyconc:
        φy = φysteel
        ξy = ξysteel[0]
    else:
        φy = φyconc
        ξy = ξyconc[0]

    if makelog:
        headers = ['', 'value', 'units']
        table = [['α', α],
                 ['Asteel', Asteel],
                 ['Bsteel', Bsteel],
                 ['ξysteel', ξysteel[0], 'm'],
                 ['φysteel', φysteel, 'm-1'],
                 ['Aconc', Aconc],
                 ['Bconc', Bconc],
                 ['ξyconc', ξyconc[0]],
                 ['φyconc', φyconc, 'm-1'],
                 ['φy', φy, 'm-1'],
                 ['ξy', ξy, 'm']]
        logtext = tabulate(table, headers, tablefmt="pipe", floatfmt=".3E")


    return α, Asteel, Bsteel, ξysteel[0], φysteel, Aconc, Bconc, ξyconc[0], φyconc, φy, ξy, logtext, latext

def A_steel(ρ1, ρ2, ρv, N, b, d, fy, makelatex=False):
    """
        Συντελεστής A για διαρροή του οπλισμού. 
        Δίνεται από τη σχέση:

        .. math::
            A=ρ+ρ'+ρ_v+\dfrac{N}{bdf_y}     
            
    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        N (float): το αξονικό φορτίο (θετικό σε θλίψη) [kN]
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος  [m]
        fy (float): το όριο διαρροής του χάλυβα  [kPa]
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]
    """
    value = ρ1 + ρ2 + ρv + N / (b * d * fy)
    if makelatex:
        # text = r"A=ρ+ρ'+ρ_v+\dfrac{{N}}{{bdf_y}}=" \
        #    + '{0:.5f}+{1:.5f}+{2:.5f}+'.format(ρ1, ρ2, ρv) \
        #    + r'\dfrac{{{0:.2f}kN}}{{{1:.2f}m\cdot{2:.2f}m\cdot{3:.1f}kPa}}={4:.5f}'.format(N, b, d, fy, value)
        text = r"A=ρ+ρ'+ρ_v+\dfrac{{N}}{{bdf_y}}=" \
           + f'{ρ1:.5f}+{ρ2:.5f}+{ρv:.5f}+' \
           + f'\dfrac{{{N:.2f}kN}}{{{b:.2f}m\cdot{d:.2f}m\cdot{fy:.1f}kPa}}={value:.5f}'
    else:
        text = ''

    return value, text


def B_steel(ρ1, ρ2, ρv, N, b, d, δtonos, fy, makelatex=False):
    """
        Συντελεστής B για διαρροή του οπλισμού. 
        Δίνεται από τη σχέση:
    
        .. math::
            B=ρ+ρ'δ'+0.5ρ_v(1+δ')+\dfrac{N}{bdf_y}
        
    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        N (float): το αξονικό φορτίο (θετικό σε θλίψη) [kN]
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος [m]
        δtonos (float): :math:`δ' = d'/d` όπου d' η απόσταση από το κέντρο του θλιβόµενου οπλισµού µέχρι την ακραία θλιβόµενη ίνα σκυροδέµατος
        fy (float): το όριο διαρροής του χάλυβα  [kPa]
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]
    """

    value = ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos) + N / (b * d * fy)
    if makelatex:
        # text = r"B=ρ+ρ'δ'+0.5ρ_v(1+δ')+\dfrac{N}{bdf_y}=" \
        #    + r'{0:.5f}+{1:.5f}\cdot{{{3:.3f}}}+0.5\cdot{2:.5f}\cdot(1+{{{3:.3f}}})+'.format(ρ1, ρ2, ρv, δtonos) \
        #    + r'\dfrac{{{0:.2f}kN}}{{{1:.2f}m\cdot{2:.2f}m\cdot{3:.1f}kPa}}={4:.5f}'.format(N, b, d, fy, value)
        text = r'\begin{aligned}' \
           + r"B &=ρ+ρ'δ'+0.5ρ_v(1+δ')+\dfrac{N}{bdf_y}=" + r'\\' \
           + f'&={ρ1:.5f}+{ρ2:.5f}\cdot{{{δtonos:.3f}}}+0.5\cdot{ρv:.5f}\cdot(1+{{{δtonos:.3f}}})+'  \
           + f'\dfrac{{{N:.2f}kN}}{{{b:.2f}m\cdot{d:.2f}m\cdot{fy:.1f}kPa}}={value:.5f}' \
           + r'\end{aligned}'
    else:
        text = ''


    return value, text


def φy_steel(fy, Es, ξy, d, makelatex=False):
    """
        Καμπυλότητα διαρροής για διαρροή του οπλισμού.
        Δίνεται από τη σχέση:
    
        .. math::        
            φ_y=\dfrac{f_y}{E_s(1-ξ_y)d}
        
    Args:
        fy (float): το όριο διαρροής του χάλυβα  [kPa]
        Es (float): το μέτρο ελαστικότητας του χάλυβα  [kPa]
        ξy (float): Το ύψος της θλιβόµενης ζώνης στη διαρροή, ανηγµένο στο στατικό ύψος d [m]
        d (float): το στατικό ύψος [m]
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]
    """

    value = fy / (Es * (1.0 - ξy) * d)
    if makelatex:
        # text = r"φ_y=\dfrac{f_y}{E_s(1-ξ_y)d}=" \
        #    + r'\dfrac{{{0:.1f}}}{{{1:.1f}(1-{2:.4f}){3:.3f}}}={4:.5f}'.format(fy, Es, ξy, d, value)
        text = r"φ_y=\dfrac{f_y}{E_s(1-ξ_y)d}=" \
           + f'\dfrac{{{fy:.1f}}}{{{Es:.1f}\cdot(1-{ξy:.4f})\cdot{d:.3f}}}={value:.5f}'
    else:
        text = ''

    return value, text


def A_conc(ρ1, ρ2, ρv, N, b, d, α, fc, makelatex=False):
    """
        Συντελεστής A για µή-γραµµικότητα των παραµορφώσεων του θλιβόµενου σκυροδέµατος
        Δίνεται από τη σχέση (χρησιμοποιείται η προσέγγιση):
    
        .. math::
            A=ρ+ρ'+ρ_v-\dfrac{N}{ε_c E_s bd}≈ρ+ρ'+ρ_v-\dfrac{N}{1.8αbdf_c}           
        
    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        N (float): το αξονικό φορτίο (θετικό σε θλίψη) [kN]
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος  [m]
        α (float): Ο λόγος των μέτρων ελαστικότητας :math:`α = E_s/E_c`
        fc (float): η θλιπτική αντοχή του σκυροδέματος  [kPa]
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]
    """
    value = ρ1 + ρ2 + ρv - N / (1.8 * α * b * d * fc)
    if makelatex:
        text = r"A=ρ+ρ'+ρ_v-\dfrac{N}{1.8αbdf_c}=" \
           + f'{ρ1:.5f}+{ρ2:.5f}+{ρv:.5f}-' \
           + f'\dfrac{{{N:.2f}kN}}{{1.8\cdot{α:.3f}\cdot{b:.2f}m\cdot{d:.2f}m\cdot{fc:.1f}kPa}}={value:.5f}'
    else:
        text = ''

    return value, text


def B_conc(ρ1, ρ2, ρv, b, d, δtonos, makelatex=False):
    """
        Συντελεστής B για µή-γραµµικότητα των παραµορφώσεων του θλιβόµενου σκυροδέµατος
         Δίνεται από τη σχέση:
    
        .. math::
            B=ρ+ρ'δ'+0.5ρ_v(1+δ')
                   
    Args:
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος  [m]
        δtonos (float): :math:`δ' = d'/d` όπου d' η απόσταση από το κέντρο του θλιβόµενου οπλισµού µέχρι την ακραία θλιβόµενη ίνα σκυροδέµατος
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]

    """
    value =  ρ1 + ρ2 * δtonos + 0.5 * ρv * (1 + δtonos)
    if makelatex:
        text = r"B=ρ+ρ'δ'+0.5ρ_v(1+δ')=" \
           + f'{ρ1:.5f}+{ρ2:.5f}\cdot{{{δtonos:.3f}}}+0.5\cdot{ρv:.5f}\cdot(1+{{{δtonos:.3f}}})={value:.5f}'
    else:
        text = ''

    return value, text


def φy_conc(fc, Ec, ξy, d, makelatex=False):
    """
        Καμπυλότητα διαρροής για για µή-γραµµικότητα των παραµορφώσεων του θλιβόµενου σκυροδέµατος
        Δίνεται από τη σχέση (χρησιμοποιείται η προσέγγιση):
        
        .. math::
            φ_y=\dfrac{ε_c}{ξ_y d}≈\dfrac{1.8 f_y}{E_s ξ_y d}
        
    Args:
        fc (float): η θλιπτική αντοχή του σκυροδέματος  [kPa]
        Ec (float): το μέτρο ελαστικότητας του σκυροδέματος  [kPa]
        ξy (float): Το ύψος της θλιβόµενης ζώνης στη διαρροή, ανηγµένο στο στατικό ύψος d [m]
        d (float): το στατικό ύψος [m]
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]
    """

    value = 1.8 * fc / (Ec * ξy * d)
    if makelatex:
        text = r"φ_y=\dfrac{1.8 f_y}{E_s ξ_y d}=" \
               + f'\dfrac{{1.8\cdot{fc:.1f}}}{{{Ec:.1f}\cdot{ξy:.4f}\cdot{d:.3f}}}={value:.5f}'
    else:
        text = ''

    return value, text





def My(b, d, φy, Ec, ξy, δtonos, ρ1, ρ2, ρv, Es, makelatex=False):
    """
        Με δεδοµένη την καµπυλότητα στη διαρροή, η αντίστοιχη ροπή Μy προκύπτει ως:
        
        .. math::
            \dfrac{M_y}{bd^3}=φ_y\Bigg\{E_c\dfrac{ξ_y^2}{2}\Big(0.5(1+δ')-\dfrac{ξ_y}{3}\Big) + \Big[ (1-ξ_y)ρ+(ξ_y-δ')ρ'+\dfrac{ρ_v}{6}(1-δ') \Big]\cdot(1-δ')\dfrac{E_s}{2} \Bigg\}

    Args:
        b (float): το πλάτος της θλιβόµενης ζώνης [m]
        d (float): το στατικό ύψος [m]
        φy (float): Καμπυλότητα διαρροής [m-1]
        Ec (float): το μέτρο ελαστικότητας του σκυροδέματος  [kPa]
        ξy (float): Το ύψος της θλιβόµενης ζώνης στη διαρροή ανηγµένο στο στατικό ύψος d
        δtonos (float): :math:`δ' = d'/d` όπου d' η απόσταση από το κέντρο του θλιβόµενου οπλισµού µέχρι την ακραία θλιβόµενη ίνα σκυροδέµατος
        ρ1 (float): (ρ) το ποσοστό του εφελκυόµενου οπλισμού
        ρ2 (float): (ρ') το ποσοστό του θλιβόμενου οπλισμού
        ρv (float): το ποσοστό του μεταξύ τους κατανεμημένου οπλισμού
        Es (float): το μέτρο ελαστικότητας του χάλυβα  [kPa]
        makelatex (bool): True για να δημιουργηθεί το latex string

    Returns:
        tuple: A tuple, with [value, latexstring]

    """
    value = b * math.pow(d, 3) * φy * (0.5 * Ec * math.pow(ξy, 2) * (0.5 * (1 + δtonos) - ξy / 3) + ((1 - ξy) * ρ1 +
        (ξy - δtonos) * ρ2 + ρv * (1 - δtonos) / 6) * (1 - δtonos) * Es / 2)
    if makelatex:
        text = r'\begin{aligned}' \
               r"M_y &=φ_ybd^3\Bigg\{E_c\dfrac{ξ_y^2}{2}\Big(0.5(1+δ')-\dfrac{ξ_y}{3}\Big) + \Big[ (1-ξ_y)ρ+(ξ_y-δ')ρ'+\dfrac{ρ_v}{6}(1-δ') \Big]\cdot(1-δ')\dfrac{E_s}{2} \Bigg\}=" + r'\\' \
               + f'&={φy:.4f}\cdot {b:.3f} \cdot {d:.3f}^3 \cdot \Bigg\{Ec:.1f}\cdot\dfrac{{{ξy:.4f}^2}}{{2}}\Big(0.5\cdot(1+{δtonos:.3f}) - \dfrac{{{ξy:.4f}}}{{3}}\Big) + ' + r'\\' \
               + f'&+ \Big[ (1-{ξy:.4f})\cdot{ρ1:.5f}+({ξy:.4f}-{δtonos:.3f})\cdot{ρ2:.5f}+\dfrac{{{ρv:.5f}}}{6}(1-{δtonos:.3f}) \Big] \cdot(1-{δtonos:.3f})\dfrac{{{Es:.1f}}}{{2}} \Bigg\}}= ' + r'\\' \
               + f'&={value:.3f}kNm' \
               + r'\end{aligned}'
    else:
        text = ''

    return value, text


# text = r'\begin{aligned}' \
#        + r"B &=ρ+ρ'δ'+0.5ρ_v(1+δ')+\dfrac{N}{bdf_y}=" + r'\\' \
#        + f'&={ρ1:.5f}+{ρ2:.5f}\cdot{{{δtonos:.3f}}}+0.5\cdot{ρv:.5f}\cdot(1+{{{δtonos:.3f}}})+' \
#        + f'\dfrac{{{N:.2f}kN}}{{{b:.2f}m\cdot{d:.2f}m\cdot{fy:.1f}kPa}}={value:.5f}' \
#        + r'\end{aligned}'