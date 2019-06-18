import numpy as np
import json


def get_scene_timesample(file_path: str,
                         t_in: float):
    """
    Python version: 3.5
    Created by: Tim Stahl
    Created on: 27.04.2019

    Documentation:  Sample script extracting scenario data for a given time instance. If the given time step is not
                    present in the data file, linear interpolation is used to generate the desired instance between the
                    neighboring time instances.

    Inputs:
    - file_path:    string holding the path to the scene data file
    - t_in:         two options:
                     * float number holding the time stamp to be extracted [linear interp. between neighboring pts]
                     * int number holding the number of the data reading to be extracted from the file

    Outputs:
    - time:         time stamp of the returned sample
    - pos:          position of the ego vehicle (list holding x and y)
    - heading:      heading of the ego vehicle (in the global frame)
    - curv:         curvature of the path at the position of the ego vehicle
    - vel:          velocity of the ego vehicle (in the direction of the heading)
    - acc:          acceleration of the ego vehicle (in the direction of the heading)
    - ego_traj:     planned ego trajectory starting at the current position (x, y, heading, vel, acc)
    - object_array: information about the vehicles in the scene (list of lists, each object holding an ID-string and a
                    list holding [x, y, pos, heading, curvature, vel, acc])
    """
    # -- get timestamps ------------------------------------------------------------------------------------------------
    time_f = np.genfromtxt(file_path, delimiter=';', skip_header=2, names=True)['time']

    if type(t_in) is int:
        idx = t_in
        if idx >= len(time_f):
            raise ValueError("Provided integer time variable is out of the range of the provided file!")
    else:
        # get timestamp before or at position of provided time step
        if time_f[0] <= t_in <= time_f[-1]:
            idx = next(x[0] for x in enumerate(time_f) if x[1] > t_in) - 1
        else:
            raise ValueError("Provided time value is out of range in provided data file!")

    # -- read relevant lines from file ---------------------------------------------------------------------------------
    header = None
    line_prev = None
    line_next = None
    with open(file_path) as fp:
        for i, line in enumerate(fp):
            if i == 2:
                line = line.replace("\n", "")
                header = line.split(";")
            elif i == idx + 3:
                line = line.replace("\n", "")
                line_prev = line.split(";")
            elif i == idx + 4:
                line = line.replace("\n", "")
                line_next = line.split(";")
                break

    # retrieve or interpolate data from file
    if type(t_in) is int or time_f[idx] == t_in or line_next is None:
        # -- extract values at current position ------------------------------------------------------------------------
        time = time_f[idx]
        pos = [float(line_prev[header.index("x")]), float(line_prev[header.index("y")])]
        heading = line_prev[header.index("heading")]
        curv = line_prev[header.index("curv")]
        vel = line_prev[header.index("vel")]
        acc = line_prev[header.index("acc")]
        ego_traj = np.array(json.loads(line_prev[header.index("ego_traj")]))
        object_array = json.loads(line_prev[header.index("object_array")])
    else:
        # -- interpolate between timestamps ----------------------------------------------------------------------------
        time = np.interp(t_in, time_f[idx:idx+2], time_f[idx:idx+2])
        pos = [np.interp(t_in, time_f[idx:idx+2], [float(line_prev[header.index("x")]),
                                                   float(line_next[header.index("x")])]),
               np.interp(t_in, time_f[idx:idx+2], [float(line_prev[header.index("y")]),
                                                   float(line_next[header.index("y")])])]

        # convert to positive values and back in order to avoid linear interpolation issues
        psi_range = np.array([float(line_prev[header.index("heading")]), float(line_next[header.index("heading")])])
        psi_range = np.where(psi_range < 0.0, psi_range + np.pi * 2, psi_range)
        heading = np.interp(t_in, time_f[idx:idx+2], psi_range)
        if heading > np.pi:
            heading -= 2 * np.pi

        curv = np.interp(t_in, time_f[idx:idx+2], [float(line_prev[header.index("curv")]),
                                                   float(line_next[header.index("curv")])])
        vel = np.interp(t_in, time_f[idx:idx+2], [float(line_prev[header.index("vel")]),
                                                  float(line_next[header.index("vel")])])
        acc = np.interp(t_in, time_f[idx:idx+2], [float(line_prev[header.index("acc")]),
                                                  float(line_next[header.index("acc")])])
        ego_traj = np.vstack((interp_1d(t_in, time_f[idx:idx+2],
                              np.array([np.array(json.loads(line_prev[header.index("ego_traj")]))[0, :],
                                        np.array(json.loads(line_next[header.index("ego_traj")]))[0, :]])),
                              np.array(json.loads(line_next[header.index("ego_traj")]))))

        object_array_prev = json.loads(line_prev[header.index("object_array")])
        object_array_next = json.loads(line_prev[header.index("object_array")])

        object_array = []
        for veh_prev, veh_next in zip(object_array_prev, object_array_next):
            object_array.append([veh_prev[0],
                                 list(interp_1d(t_in, time_f[idx:idx+2], np.array([veh_prev[1], veh_next[1]])))])

    return time, pos, heading, curv, vel, acc, ego_traj, object_array


def interp_1d(x, xp, fp_array: np.ndarray):
    """
    extends the functionality of numpy's 'interp' to an array like structure
    """
    y_array = np.zeros(fp_array.shape[1])
    for col in range(fp_array.shape[1]):
        y_array[col] = np.interp(x, xp, fp_array[:, col])

    return y_array


# -- main --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    z = get_scene_timesample(file_path="C:/Users/ga79jix/Documents/Forschung/scenario-generator/temp.scn",
                             t_in=4.0)
    print(z)
