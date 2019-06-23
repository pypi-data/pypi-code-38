import numpy as np



def scale_grid(N, map_scale):
    '''
    Create an N*N*2 array where each elements specify the pixel's coordinates (in
    arcsec).
    map_scale: pixel_scale [arcsec/pixel]
    '''
    std_line_angle = map_scale*np.arange(-(N-1)/2, (N+1)/2, 1)
    theta = np.zeros((N, N, 2))
    n1 = np.tile(std_line_angle, N)
    theta[:, :, 1] = n1.reshape((N, N))
    n2 = np.repeat(-std_line_angle, N)
    theta[:, :, 0] = n2.reshape((N, N))
    return theta.copy()

def deflection_multi_map(N, map_scale, tracer, z_lens, z_source):
    '''
    Calculate deflection angle: alpha = theta - beta
    theta are coordinates of grids
    beta are deflected coordinates of grids
    '''
    theta = scale_grid(N=N, map_scale=map_scale)
    theta = theta.copy()
    theta_1d = theta.reshape((-1, 2)).copy()
    beta_1d = tracer.grid_at_redshift_from_image_plane_grid_and_redshift(
            theta_1d, redshift=z_source)
    print(beta_1d)
    alpha_1d_unscale = theta_1d - beta_1d
    alpha_unscale = alpha_1d_unscale.reshape((N, N, 2))
    alpha = alpha_unscale.copy()
    return alpha.copy()