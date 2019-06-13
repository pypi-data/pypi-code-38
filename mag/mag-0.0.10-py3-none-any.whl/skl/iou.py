'''

index:   0  1  2  3  4  5  6  7  8  9  10 11 12 13 14   [ lower, upper ]
pred1:   |-----------------------|                      [     0,     8 ]
targ1:                     |------------------------|   [     6,    14 ] (expected)

pred2:   |-----------|                                  [     0,     4 ]
targ2:                     |------------------------|   [     6,    14 ] (no overlap)

pred3:   |-----------------------|                      [     0,     8 ]
targ3:                     ||                           [     6,     6 ] (small sequence)

pred4:                     |---------------------|      [     6,    13 ]
targ4:                     |---------------------|      [     6,    13 ] (perfect match)

pred5:                     ||                           [     6,     6 ]
targ5:                     ||                           [     6,     6 ] (perfect match, small sequence)

pred6:                 ||                               [     5,     5 ]
targ6:                     ||                           [     6,     6 ] (mismatch, both small sequence)

pred7:              ||                                  [     4,     4 ]
targ7:                     |------------------------|   [     6,    14 ] (mismatch, one small sequence)


I = min(p_upper, t_upper) - max(p_lower, t_lower)
U = max(p_upper, t_upper) - min(p_lower, t_lower)

i1 = min( 8, 14) - max(0, 6) =  8 - 6 =  2
u1 = max( 8, 14) - min(0, 6) = 14 - 0 = 14  --(IOU)-->  2 / 14 [√] makes sense

i2 = min( 4, 14) - max(0, 6) =  4 - 6 = -2
u2 = max( 4, 14) - min(0, 6) = 14 - 0 = 14  --(IOU)--> -2 / 14 [ ] ERROR should be 0?

i3 = min( 8,  6) - max(0, 6) =  6 - 6 =  0
u3 = max( 8,  6) - min(0, 6) =  8 - 0 =  8  --(IOU)-->  0 /  8 [ ] ERROR, should be 1 / 8

i4 = min(13, 13) - max(6, 6) = 13 - 6 =  7
u4 = max(13, 13) - min(6, 6) = 13 - 6 =  7  --(IOU)-->  7 /  7 [√] makes sense

i5 = min( 6,  6) - max(6, 6) =  6 - 6 =  0
u5 = max( 6,  6) - min(6, 6) =  6 - 6 =  0  --(IOU)-->  0 /  0 [ ] ERROR, just return 0

i6 = min( 5,  6) - max(5, 6) =  5 - 6 = -1
u6 = max( 5,  6) - min(5, 6) =  6 - 5 =  1  --(IOU)--> -1 /  1 [ ] ERROR, should be 0?


i7 = min( 4, 14) - max(4, 6) =  4 - 6 = -2
u7 = max( 4, 14) - min(4, 6) = 14 - 4 = 10  --(IOU)--> -2 / 10 [ ] ERROR should be 0?

We can define 5 unique cases:

1. expected, the sequences overlap (example 1)
2. no overlap (examples 2, 6, 7)
3. perfect (example 4)
4. perfect, small sequences (example 5)
5. expected, but with one small sequence (example 3)

For case 1 and 3 we can trust our formula.
For case 4 we can just return 1
For case 5 we need to add 1 to the intersection
For case 2 we return 0?


'''
def iou_1d(predicted_boundary, target_boundary):
    '''Calculates the intersection over union (IOU) based on a span.

    Notes:
        boundaries are provided in the the form of [start, stop].
        boundaries where start = stop are accepted
        boundaries are assumed to be only in range [0, int < inf)

        if no intersection, returns 0.


    Example:

        0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 index
           |-----------------------|                                   predicted
                             |------------------------|                target

        then the predicted boundaries are:

            [ lower, upper ]
            [     1,     9 ] predicted
            [     7,    15 ] target

        then the intersection of these two sequences would be:

             2 = 9 - 7
               = min(9, 15) - max(1, 7)
               = min(p_upper, t_upper) - max(p_lower, t_lower)

        and the union:

            14 = 15 - 1
               = max(15, 9) - min(7, 1)
               = max(t_upper, p_upper) - min(t_lower, p_lower)

        giving as IOU of:

            0.143 ≈ 1 / 7 =  2 / 14

    Args:
        predicted_boundary (list): the [start, stop] of the predicted boundary
        target_boundary (list): the ground truth [start, stop] for which to compare

    Returns:
        iou (float): the IOU bounded in [0, 1]

    '''

    p_lower, p_upper = predicted_boundary
    t_lower, t_upper = target_boundary

    # boundaries are in form [start, stop] and 0 <= start <= stop
    assert 0<= p_lower <= p_upper
    assert 0<= t_lower <= t_upper

    # no overlap, pred is too far left or pred is too far right
    if p_upper < t_lower or p_lower > t_upper:
        # handle case 2
        return 0

    if predicted_boundary == target_boundary:
        # handle case 3 and 4
        return 1

    intersection_lower_bound = max(p_lower, t_lower)
    intersection_upper_bound = min(p_upper, t_upper)

    intersection = intersection_upper_bound - intersection_lower_bound

    max_upper = max(t_upper, p_upper)
    min_lower = min(t_lower, p_lower)

    union = max_upper - min_lower

    if intersection == 0:
        # handle case 5
        intersection = 1

    # return case 1
    return intersection / union
