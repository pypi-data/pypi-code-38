import math

def distance(ck1, ck2, weights=None):
    """
    Compute the cocktail distance coefficient between cocktails.

    This function implements the cocktails distance coefficient defined as:

    .. math:: CD_{coeff}(i,j) = \\frac{1}{sum(w)}\\Biggl(\\Bigl(\\frac{\\left|E(pH_{i})-E(pH_{j})\\right|}{14}\\Bigr)w_{1}+BC(F_{i},F_{j})w_{2}\\Biggr)

    Where :math:`w=\\left\\{w_{1},w_{2}\\right\\}` are weights, :math:`w_{k} \\ge 0`, :math:`sum(w) > 0`. :math:`F_{i}` is the fingerprint of cocktail
    :math:`i` and :math:`E(pH_{i})` is n estimate of the pH in condition :math:`i` normalized by a maxium pH of 14. :math:`BC(F_{i},F_{j})` is the 
    Bray-Curtis dissimilarity measure between cocktail fingerprints :math:`i` and :math:`j`. 


    """

    # Default to equal weights
    if weights is None: 
        w = [1.0,1.0]
    else:
        w = weights[:]

    ph = ph_distance(ck1, ck2)
    if ph is None:
        ph = 0
        w[0] = 0

    fp = fp_distance(ck1, ck2)
    if fp is None:
        fp = 0
        w[1] = 0

    # If all weights are 0, then technically it's undefined but we default to
    # max dissimilarity 
    if sum(w) == 0: return 1

    return ( (w[0]*ph) + (w[1]*fp) ) / sum(w)

def _braycurtis(fp1, fp2):
    """
    Compute the Bray-Curtis dissimilarity measure between fingerprint vectors.

    :returns: distance between 0 and 1
    """
    diff_sum = 0
    summ = 0
    for k in list(set(list(fp1.keys()) + list(fp2.keys()))):
        a = fp1.get(k, 0)
        b = fp2.get(k, 0)
        diff_sum += math.fabs(a - b)
        summ += math.fabs(a + b)

    if summ == 0: return 1

    return float(diff_sum)/float(summ)


def fp_distance(ck1, ck2):
    """
    Compute distance between fingerprint vectors

    :param cocktail ck1: First cocktail to compare
    :param cocktail ck2: Second cocktail to compare

    :returns: The distance score between 0 and 1, or None if either cocktail is missing a fingerprint
        
    """
    # either missing: undefined
    if ck1.fingerprint() is None or ck2.fingerprint() is None:
        return None


    return _braycurtis(ck1.fingerprint(), ck2.fingerprint())

def ph_distance(ck1, ck2):
    """
    Compute pH distance.

    :param cocktail ck1: First cocktail to compare
    :param cocktail ck2: Second cocktail to compare

    :returns: The distance score between 0 and 1 or None if cocktails are missing pH
        
    """
    # either missing: undefined
    if ck1.ph is None or ck2.ph is None: 
        return None

    return math.fabs(ck1.ph - ck2.ph) / 14.0
