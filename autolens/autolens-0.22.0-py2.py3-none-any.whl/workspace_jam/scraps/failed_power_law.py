# @geometry_profiles.transform_grid
# def deflections_from_grid_2(self, grid):
#     self.slope = self.slope - 1
#     #   eta = self.grid_to_radius(grid)
#     norm = 2 * self.einstein_radius * np.sqrt(self.axis_ratio) / (1 + self.axis_ratio)
#     eta = np.sqrt((self.axis_ratio ** 2 * grid[:, 1] ** 2 + grid[:, 0] ** 2)) / (
#             self.einstein_radius * np.sqrt(self.axis_ratio))
#     radial_part = norm * (eta) ** (1 - self.slope)
#
#     order = 20
#     phi = np.arctan2(self.axis_ratio * grid[:, 1], grid[:, 0])  # The numpy arctan2 function is identical to atan2 in C
#     cos = np.cos(2 * phi)
#     sin = np.sin(2 * phi)
#     f = (1 - self.axis_ratio) / (1 + self.axis_ratio)
#     T = 2 - self.slope
#     nx = grid.shape[0]
#     ny = grid.shape[0]
#     omega_x = np.zeros((ny, nx, order))
#     omega_y = np.zeros((ny, nx, order))
#     omega_x[:, :, 0] = np.cos(phi)
#     omega_y[:, :, 0] = np.sin(phi)
#     for n in range(1, order):
#         omega_x[:, :, n] = - f * (2 * n - T) / (2 * n + T) * (
#                 cos * omega_x[:, :, n - 1] - sin * omega_y[:, :, n - 1])
#         omega_y[:, :, n] = - f * (2 * n - T) / (2 * n + T) * (
#                 sin * omega_x[:, :, n - 1] + cos * omega_y[:, :, n - 1])
#     angular_part_x = np.sum(omega_x, axis=2)
#     angular_part_y = np.sum(omega_y, axis=2)
#     #	Deflection angle = radial part * angular part
#
#     return self.rotate_grid_from_profile(np.multiply(1.0, np.vstack((radial_part * angular_part_y,
#                                                                      radial_part * angular_part_x)).T))