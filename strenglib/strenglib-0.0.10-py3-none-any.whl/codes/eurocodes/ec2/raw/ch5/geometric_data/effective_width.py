""" Beams effective width
"""

def beff(bw, beff1, beff2, b):
    """ Effective flange width

        .. image:: http://repfiles.kallipos.gr/html_books/1284/images/Fig_09_14.png

    Args:
        bw (float): Width of the web
        beff1 (float): Side 1 effective flange width
        beff2 (float): Side 2 effective flange width
        b (float): bw + b1 + b2

    Returns:
        float: Given using the expression:

        .. math::
            b_{eff}=\sum{b_{eff,i}} + b_w \le b

    """
    return min(bw + beff1 + beff2, b)


def beffi(bi, l0):
    """ Side i effective flange width

        .. image:: http://repfiles.kallipos.gr/html_books/1284/images/Fig_09_14.png

    Args:
        bi (float): half net length between adjacent beams
        l0 (float): Distance between points of zero moment

    Returns:
        float: Given using the expression:

        .. math::
            b_{eff,i}=0.2\cdot b_i +0.1\cdot l_0 \le 0.2\cdot l_0

    """
    return min(0.2 * bi + 0.1 * l0, 0.2 * l0, bi)


def l0(l1 =0 , l2 = 0, l3 = 0, zero_moments_case = 0):
    """ Distance between points of zero moment

        .. image:: http://repfiles.kallipos.gr/html_books/1284/images/inter_09_01_2.png

    Args:
        l1 (float): μήκος αμφιέρειστης ή ακραίου ανοίγματος
        l2 (float): μήκος μεσαίουν ανοίγματος
        l3 (float): μήκος προβόλου
        b (float): συνθήκες στήριξης. 0: αμφιέρειστη, 1: ακραίο άνοιγμα, 2: μεσαίο άνοιγμα, 3: μεσαία στήριξη, 4: στήριξη προβόλου

    Returns:
        float: Υποπεριπτώσεις σύμφωνα με το σχήμα


    """
    _l0 = 0
    if zero_moments_case==0: _l0 = 1.00 * l1 # αμφιέρειστη
    if zero_moments_case==1: _l0 = 0.85 * l1 # ακραίο άνοιγμα
    if zero_moments_case==2: _l0 = 0.70 * l2 # μεσαίο άνοιγμα
    if zero_moments_case==3: _l0 = 0.15 * (l1 + l2) # μεσαία στήριξη
    if zero_moments_case==4: _l0 = 0.15 * l2 + l3 # στήριξη προβόλου

    return _l0
