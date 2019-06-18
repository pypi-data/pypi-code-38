import numpy as np
import json
from matplotlib import pyplot


def get_scene_track(file_path: str):
    """
    Python version: 3.5
    Created by: Tim Stahl
    Created on: 21.05.2019

    Documentation:  Sample script extracting the track bounds from a scene file.

    Inputs:
    - file_path:    string holding the path to the scene data file

    Outputs:
    - bound_{l/r}:  coordinates of the tracks bounds {left / right}
    """
    # -- read relevant lines from file ---------------------------------------------------------------------------------
    bound_l = None
    bound_r = None
    with open(file_path) as fp:
        for i, line in enumerate(fp):
            if 'bound_l' in line:
                line = line.replace("# bound_l:", "")
                bound_l = np.array(json.loads(line))
            elif 'bound_r' in line:
                line = line.replace("# bound_r:", "")
                bound_r = np.array(json.loads(line))
            else:
                break

    if bound_l is None or bound_r is None:
        raise ValueError("Something went wrong, while extracting the bound data from the provided file! Check if the"
                         "first two lines of the file hold boundary information.")

    return bound_l, bound_r


def get_scene_occupancy(file_path: str,
                        grid_res: float = 0.1,
                        x_range: tuple = (0.0, 100.0),
                        y_range: tuple = (0.0, 100.0),
                        plot_occupancy=False):
    """
    Python version: 3.5
    Created by: Tim Stahl
    Created on: 22.05.2019

    Documentation:  Sample script generating an occupancy grid from the bounds stored in a scene file.

    Inputs:
    - file_path:    string holding the path to the scene data file
    - grid_res:     resolution of the occupancy grid (cell width / height in meters)
    - {x/y}_range:  coordinate range of the occupancy grid to be generated (start and end coordinate, respectively)
    - plot_occupancy: flag, determining whether or not to visualize the occupancy grid

    Outputs:
    - occ_grid:     occupancy grid (numpy array) holding ones for occupied cells and zeros for unoccupied cells
    - origin:       x, y coordinates of the origin (0, 0) in the occupancy grid

    NOTE: The returned occupancy grid holds the standard specs of an image! Therefore, the origin (0, 0) is in the upper
          left corner. Furthermore, the y-axis is given first!
    """

    # get bound coordinates from file
    bound_l, bound_r = get_scene_track(file_path)

    # initialize matrix of occupancy grid (use predefined min and max bounds)
    origin = [x_range[0], y_range[1]]
    occ_grid = np.zeros((int((y_range[1]-y_range[0])/grid_res), int((x_range[1]-x_range[0])/grid_res)))

    for bound in [bound_l, bound_r]:
        for i in range(bound.shape[0] - 1):
            bound_s_x = bound[i][0]
            bound_e_x = bound[i+1][0]
            bound_s_y = bound[i][1]
            bound_e_y = bound[i+1][1]

            # get number of samples (maximum of steps required for each of the coordinates)
            n_steps = int(np.ceil(max(np.abs(bound_e_x - bound_s_x)/grid_res,
                                      np.abs(bound_e_y - bound_s_y)/grid_res))) * 2

            # linear interpolation for each coordinate (finer than grid resolution)
            x_steps = np.linspace(bound_s_x, bound_e_x, n_steps)
            y_steps = np.linspace(bound_s_y, bound_e_y, n_steps)

            # loop through all coordinates and set the corresponding bins to one
            for j in range(n_steps):
                x_idx = int((origin[1] - y_steps[j])/grid_res)
                y_idx = int((x_steps[j] - origin[0])/grid_res)

                # if index in bounds of occupancy grid
                if 0 <= x_idx < occ_grid.shape[0] and 0 <= y_idx < occ_grid.shape[1]:
                    occ_grid[x_idx, y_idx] = 1.0

    # plot occupancy, if flag is set
    if plot_occupancy:
        pyplot.imshow(occ_grid, aspect='equal', cmap='Greys')
        pyplot.show()

    return occ_grid, origin


# -- main --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    z = get_scene_occupancy(file_path="C:/Users/ga79jix/Documents/Forschung/scenario-generator/temp.scn",
                            x_range=(0.0, 100.0),
                            y_range=(0.0, 100.0),
                            plot_occupancy=True)
    print(z)
