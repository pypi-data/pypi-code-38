import os, math, numpy as np, cv2
from math import factorial

def list_folders_in_path(path):
    if not os.path.exists(path): return []
    return sorted([os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])

def list_files_in_path(path):
    if not os.path.exists(path): return []
    return sorted([os.path.join(path, d) for d in os.listdir(path) if not os.path.isdir(os.path.join(path, d))])

def points_angle(p1, p2): 
    x1, y1 = p1
    x2, y2 = p2
    rads = math.atan2(y2-y1,x2-x1)
    return rads

def min_dist_angles(ang1, ang2):
    tmp  = max(ang1, ang2)
    ang2 = min(ang1, ang2)
    ang1 = tmp
    angle1 = abs(ang1-ang2)
    angle2 = abs(ang1-(np.pi*2)-ang2)
    angle3 = abs(ang1+(np.pi*2)-ang2)
    return min(angle1, angle2, angle3)

def lin_dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)


def savitzky_golay(y, window_size, order=0, deriv=0, rate=1):
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError as msg:
        raise ValueError("window_size and order have to be of type int")
    if (window_size % 2 != 1) or (window_size < 1):
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    if deriv>order:
        raise TypeError("order is too small for rate")
        
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')








def getTranslationMatrix2d(dx, dy):
    """
    Returns a numpy affine transformation matrix for a 2D translation of
    (dx, dy)
    """
    return np.matrix([[1, 0, dx], [0, 1, dy], [0, 0, 1]])


def rotate_image(image, angle, image_center=None):
    """
    Rotates the given image about it's centre
    """

    image_size = (image.shape[1], image.shape[0])
    if image_center is None:
        image_center = tuple(np.array(image_size) / 2)

    rot_mat = np.vstack([cv2.getRotationMatrix2D(image_center, angle, 1.0), [0, 0, 1]])
    trans_mat = np.identity(3)

    w2 = image_size[0] * 0.5
    h2 = image_size[1] * 0.5

    rot_mat_notranslate = np.matrix(rot_mat[0:2, 0:2])

    tl = (np.array([-w2, h2]) * rot_mat_notranslate).A[0]
    tr = (np.array([w2, h2]) * rot_mat_notranslate).A[0]
    bl = (np.array([-w2, -h2]) * rot_mat_notranslate).A[0]
    br = (np.array([w2, -h2]) * rot_mat_notranslate).A[0]

    x_coords = [pt[0] for pt in [tl, tr, bl, br]]
    x_pos = [x for x in x_coords if x > 0]
    x_neg = [x for x in x_coords if x < 0]

    y_coords = [pt[1] for pt in [tl, tr, bl, br]]
    y_pos = [y for y in y_coords if y > 0]
    y_neg = [y for y in y_coords if y < 0]

    right_bound = np.max(x_pos)
    left_bound = np.min(x_neg)
    top_bound = np.max(y_pos)
    bot_bound = np.min(y_neg)

    new_w = int(np.abs(right_bound - left_bound))
    new_h = int(np.abs(top_bound - bot_bound))
    new_image_size = (new_w, new_h)

    new_midx = new_w * 0.5
    new_midy = new_h * 0.5

    dx = int(new_midx - w2)
    dy = int(new_midy - h2)

    trans_mat = getTranslationMatrix2d(dx, dy)
    affine_mat = (np.matrix(trans_mat) * np.matrix(rot_mat))[0:2, :]
    result = cv2.warpAffine(image, affine_mat, new_image_size, flags=cv2.INTER_LINEAR)

    return result