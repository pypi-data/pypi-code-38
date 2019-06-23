import math


def θy(φy, Ls, av, z, h, db, fy, fc, units='m-MPa'):
    """ Στροφή διαρροής

    .. highlight:: python
    .. code-block:: python
       :linenos:

        theta = rotation.θy(φy=0.00638,
                            Ls=2.525,
                            av=1,
                            z=0.506,
                            h=0.506,
                            db=0.018,
                            fy=500.,
                            fc=16,
                            units='m-MPa')

    Args:
        φy (float): Καμπυλότητα διαρροής [m-1]
        Ls (float): Μήκος διάτμησης [m]
        av (int): συντελεστής που ισούται με 1 εάν η τέμνουσα VRc που προκαλεί λοξή ρηγμάτωση του στοιχείου,
            υπολείπεται της τιμής της τέμνουσας κατά την καμπτική διαρροή VMu=My/Ls, και με 0 αν είναι μεγαλύτερη
        z (float): Ο μοχλοβραχίονας των εσωτερικών δυνάμεων
        h (float): το ύψος της διατομής [m]
        db (float): η διάμετρος των διαμήκων ράβδων [m]
        fy (float): το όριο διαρροής του χάλυβα [MPa]
        fc (float): η θλιπτική αντοχή του σκυροδέματος [MPa]

    Returns:
        float: Given using the expression:

        .. math:: θ_y=φ_y\dfrac{L_s+a_vz}{3}+0.0014 \Big(1+1.5\dfrac{h}{L_s} \Big)+\dfrac{φ_yd_bf_y}{8\sqrt{f_c}}
    """
    return φy * (Ls + av * z) / 3 + 0.0014 * (1 + 1.5 * h / Ls) + φy * db * fy / (8 * fc**0.5)


def θum(ν, ωtot, ω2, αs, α, ρs, ρd, fc, fyw, units='MPa'):
    """ Στροφή αστοχίας θum

     .. highlight:: python
     .. code-block:: python
        :linenos:

        theta_u = rotation.θum(ν=0.093,
                               ωtot=0.351,
                               ω2=0.132,
                               αs=3.78,
                               α=0.4737,
                               ρs=0.00279,
                               ρd=0.,
                               fc=16.,
                               fyw=500.,
                               units='MPa')

     Args:
         ν (float): ανηγμένο αξονικό
         ωtot (float): Συνολικό μηχανικό ποσοστό οπλισμού
         ω2 (float): Μηχανικό ποσοστό θλιβόμενου οπλισμού
         αs (float): Λόγος διάτμησης
         ρs (float): Γεωμετρικό ποσοστό εγκάρσιου οπλισμού
         ρd (float): Γεωμετρικό ποσοστό δισδιαγώνιου οπλισμού
         fc (float): η θλιπτική αντοχή του σκυροδέματος [MPa]
         fyw (float): το όριο διαρροής του χάλυβα ου εγκάρσιου οπλισμού [MPa]

     Returns:
         float: Given using the expression:

         .. math:: θ_{um}=0.016\cdot(0.3^ν)\cdot\Bigg[\dfrac{max(0.01,ω')}{max(0.01, (ω_{tot}-ω'))} \cdot f_c\Bigg]^{0.225}\cdot (α_s)^{0.35} \cdot 25^{(α\cdot ρ_s \cdot \dfrac{f_{yw}}{f_c})}\cdot (1.25^{100ρ_d})

     """
    part1 = (fc * max(0.01, ω2) / max(0.01, (ωtot-ω2)))**0.225
    part2 = αs**0.35
    part3 = 25.0**(α * ρs * fyw / fc)
    part4 = 1.25**(100 * ρd)
    return 0.016 * 0.3**ν * part1 * part2 * part3 * part4


def αcalc(sh, bc, hc, Σbi2):
    return (1-sh/(2*bc))*(1-sh/(2*hc))*(1-Σbi2/(6*bc*hc))