def collideTrajectory(pt, origin, trajectory, tolerance):
    '''Returns true if pt lies within a distance of tolerance from the
    line segment described by origin and trajectory.'''

    # Get distance between point and trajectory origin.
    tr0 = origin
    d0 = ((tr0[0] - pt[0]) ** 2 + (tr0[1] - pt[1]) ** 2) ** 0.5
    if d0 < tolerance:
        return True

    delta = trajectory

    while True:
        # Calculate other end of trajectory.
        tr1 = (tr0[0] + delta[0],
               tr0[1] + delta[1])
        d1 = ((tr1[0] - pt[0]) ** 2 + (tr1[1] - pt[1]) ** 2) ** 0.5

        # Check for collision.
        if d1 < tolerance:
            return True

        # Refine and loop.
        if d1 < d0:
            tr0, delta = tr1, (-0.5 * delta[0],
                               -0.5 * delta[1])
        else:
            delta = (0.5 * delta[0],
                     0.5 * delta[1])

        # Check end condition.
        if (delta[0] ** 2 + delta[1] ** 2) < 5:
            return False
