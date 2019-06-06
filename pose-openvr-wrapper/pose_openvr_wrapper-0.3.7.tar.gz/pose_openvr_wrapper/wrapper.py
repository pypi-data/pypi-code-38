#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""Convenient and simple wrapper of pyopenvr Library.

DESCRIPTION
===========
The focus is given on the easy acces of one specific pose transformation,

FILES
=====
Reads a file, ''config.json''. :: Which is required for keeping devices numbers
 consistent with their respectives serials numbers

AUTHOR
======
Virgile Daugé
"""

import sys
import json
import time
import math
import openvr
import numpy as np
from pose_transform import Transform


class OpenvrWrapper():
    """OpenvrWrapper is keeping track of connected vr devices.

    DESCRIPTION
    ===========
    OpenVRWrapper is design to easily retrieve poses of tracked devices.
    It has no intend to do anything else,
    so it's not covering any other part of openvr Library.
    """

    def __init__(self, path='config.json'):
        """Start and Scan VR devices."""
        # Initialize OpenVR
        self.vr = openvr.init(openvr.VRApplication_Other)

        # Loading config file
        self.config = None
        try:
            with open(path) as json_data:
                self.config = json.load(json_data)
        except EnvironmentError:  # parent of IOError, OSError
            print('required config.json not found, closing...')
            openvr.shutdown()
            sys.exit(1)

        poses = self.vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

        """Adding connected devices according to the loaded config file.::
        Iterate through the pose list to find the active devices and
        determine their type."""
        self.devices = {}
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            if poses[i].bPoseIsValid:
                device_serial = self.vr.getStringTrackedDeviceProperty(
                    i, openvr.Prop_SerialNumber_String).decode('utf-8')

                for device in self.config['devices']:
                    if device_serial == device['serial']:
                        self.devices[device['name']] = device
                        device['index'] = i

    def get_transformation_matrix(self, target_device_key, ref_device_key=None,
                                  samples_count=1000, sampling_frequency=250):
        """Retrive selected transformation from openvr.

        It can be relative or not.
        Relative is if you want particular transformation between two devices.
        Given time is only elapsed time from beginning of sampling.

        :param target_device_key: the key of target device (default None)
        :param ref_device_key: the key of reference device (relative result)
        :param samples_count: the desired number of samples to read
        :param sampling_frequency: the desired sampling frequency (does not
        change the devices update frequency, just the frequency at which
        we get data)

        :type target_device_key: str
        :type ref_device_key: str
        :type samples_count: int, float,...
        :type sampling_frequency: int, float,...
        :returns: meaned data in transformation_matrix format
        :rtype: numpy ndarray
        """
        if samples_count == 1:
            return self.get_pose(
                target_device_key=target_device_key,
                ref_device_key=ref_device_key)
        if sampling_frequency is 0:
            sampling_frequency = 1

        interval = 1./sampling_frequency
        matrices = []
        for i in range(samples_count):
            start = time.time()
            matrices.append(self.get_pose(target_device_key=target_device_key,
                            ref_device_key=ref_device_key))

            # Computes elapsed time to sleep according to selected frequency
            sleep_time = interval - (time.time()-start)
            if sleep_time > 0:
                time.sleep(sleep_time)
        return np.mean(matrices, axis=0)

    def get_all_transformation_matrices(self, ref_device_key=None,
                                        samples_count=1000,
                                        sampling_frequency=250):
        """Retrive all transformation from openvr in right hand convention.

        It can be relative or not.
        Relative is if you want particular transformation between two devices.
        Given time is only elapsed time from beginning of sampling.

        :param ref_device_key: the key of reference device (relative result)
        :param samples_count: the desired number of samples to read
        :param sampling_frequency: the desired sampling frequency (does not
        change the devices update frequency, just the frequency at which
        we get data)

        :type ref_device_key: str
        :type samples_count: int, float,...
        :type sampling_frequency: int, float,...
        :returns: dict with all transformation matrices
        :rtype:  python dict
        """

        if sampling_frequency is 0:
            sampling_frequency = 1

        interval = 1./sampling_frequency

        stack_dict = {device: [] for device in self.devices}

        if samples_count == 1:
            poses_dict = {}
            poses = self.vr.getDeviceToAbsoluteTrackingPose(
                openvr.TrackingUniverseStanding, 0,
                openvr.k_unMaxTrackedDeviceCount)
            for device in self.devices:
                target_id = self.devices[device]['index']
                if poses[target_id].bPoseIsValid:
                    poses_dict[device] = np.concatenate((
                        poses[target_id].mDeviceToAbsoluteTracking.m,
                        [[0, 0, 0, 1]]))
            if ref_device_key is None:
                return poses_dict
            else:
                relative_dict = {}
                inv_ref_matrix = np.linalg.inv(poses_dict[ref_device_key])
                for device in self.devices:
                    if device != ref_device_key:
                        relative_dict[device] = inv_ref_matrix.dot(
                            poses_dict[device])
                return relative_dict
        else:
            for i in range(samples_count):
                start = time.time()
                poses = self.vr.getDeviceToAbsoluteTrackingPose(
                    openvr.TrackingUniverseStanding, 0,
                    openvr.k_unMaxTrackedDeviceCount)
                for device in self.devices:
                    target_id = self.devices[device]['index']
                    if poses[target_id].bPoseIsValid:
                        stack_dict[device].append(np.concatenate((
                            poses[target_id].mDeviceToAbsoluteTracking.m,
                            [[0, 0, 0, 1]])))
                # Computes elapsed time to sleep according to selected frequency
                sleep_time = interval - (time.time()-start)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            meaned_dict = {d: self.correct_transformation_matrix(
                np.mean(m, axis=0)) for d, m in stack_dict.items() if len(m) > 0}

            if ref_device_key is None:
                return meaned_dict
            else:
                relative_dict = {}
                inv_ref_matrix = np.linalg.inv(meaned_dict[ref_device_key])
                for device in self.devices:
                    if device != ref_device_key:
                        relative_dict[device] = inv_ref_matrix.dot(
                            meaned_dict[device])
                return relative_dict

    def get_corrected_transformation_matrix(self, target_device_key,
                                            ref_device_key=None,
                                            samples_count=1000,
                                            sampling_frequency=250):
        """Retrive and correct selected transformation from openvr.

        Here the "correction" is to replace it in a real world right handed
        convention, not in the vive specific convention
        (for use in robotics for instance)

        It can be relative or not.
        Relative is if you want particular transformation between two devices.
        Given time is only elapsed time from beginning of sampling.

        :param target_device_key: the key of target device (default None)
        :param ref_device_key: the key of reference device (relative result)
        :param samples_count: the desired number of samples to read
        :param sampling_frequency: the desired sampling frequency (does not
        change the devices update frequency, just the frequency at which
        we get data)

        :type target_device_key: str
        :type ref_device_key: str
        :type samples_count: int, float,...
        :type sampling_frequency: int, float,...
        :returns: corected data in transformation_matrix format
        :rtype: numpy ndarray
        """
        matrix = self.get_transformation_matrix(
            target_device_key=target_device_key,
            ref_device_key=ref_device_key,
            samples_count=samples_count,
            sampling_frequency=sampling_frequency)
        # correction_matrix = np.array([[1, 0, 0, 0],
        #                              [0, 0, -1, 0],
        #                              [0, 1, 0, 0],
        #                              [0, 0, 0, 1]])
        #
        # matrix = correction_matrix.dot(matrix)
        # # recalage du repère
        # x_rotation = np.array([[1, 0, 0],
        #                       [0, 0, 1],
        #                       [0, -1, 0]])
        # matrix[:3, :3] = matrix[:3, :3].dot(x_rotation)
        return self.correct_transformation_matrix(matrix)

    def correct_transformation_matrix(self, matrix):
        corrected_matrix = np.copy(matrix)
        correction_matrix = np.array([[1, 0, 0, 0],
                                     [0, 0, -1, 0],
                                     [0, 1, 0, 0],
                                     [0, 0, 0, 1]])

        corrected_matrix = correction_matrix.dot(
            corrected_matrix)
        # recalage du repère
        x_rotation = np.array([[1, 0, 0],
                              [0, 0, 1],
                              [0, -1, 0]])
        corrected_matrix[:3, :3] = corrected_matrix[:3, :3].dot(x_rotation)
        return corrected_matrix

    def sample(self, target_device_key, ref_device_key=None,
               samples_count=1000, sampling_frequency=250):
        """Retrive and format selected transformation from openvr.

        It can be relative or not.
        Relative is if you want particular transformation between two devices.
        Given time is only elapsed time from beginning of sampling.

        :param target_device_key: the key of target device (default None)
        :param ref_device_key: the key of reference device (relative result)
        :param samples_count: the desired number of samples to read
        :param sampling_frequency: the desired sampling frequency (does not
        change the devices update frequency, just the frequency at which
        we get data)

        :type target_device_key: str
        :type ref_device_key: str
        :type samples_count: int, float,...
        :type sampling_frequency: int, float,...
        :returns: all measured data in both raw and more understandable format
        :rtype: dict
        """
        if sampling_frequency is 0:
            sampling_frequency = 1

        interval = 1./sampling_frequency
        rtn = {'time': [], 'x': [], 'y': [], 'z': [],
               'r_x': [], 'r_y': [], 'r_z': [], 'r_w': [],
               'roll': [], 'pitch': [], 'yaw': [],
               'matrix': []}

        sample_start = time.time()
        for i in range(samples_count):
            start = time.time()
            mat = self.get_pose(target_device_key=target_device_key,
                                ref_device_key=ref_device_key)
            # Append to dict
            rtn['time'].append(time.time()-sample_start)
            # Saving raw transformation matrix
            rtn['matrix'].append(np.asarray(mat))
            # Translation vector
            rtn['x'].append(mat[0][3])
            rtn['y'].append(mat[1][3])
            rtn['z'].append(mat[2][3])

            # Computes euler angles from rotation matrix
            rtn['yaw'].append(180 / math.pi * math.atan(mat[1][0] /
                                                        mat[0][0]))
            rtn['pitch'].append(180 / math.pi * math.atan(
                -1 * mat[2][0] / math.sqrt(pow(mat[2][1], 2) +
                                           math.pow(mat[2][2], 2))))
            rtn['roll'].append(180 / math.pi * math.atan(mat[2][1] /
                                                         mat[2][2]))

            # Computes quaternion from rotation matrix
            r_w = math.sqrt(abs(1+mat[0][0]+mat[1][1]+mat[2][2]))/2
            rtn['r_w'].append(r_w)
            rtn['r_x'].append((mat[2][1]-mat[1][2])/(4*r_w))
            rtn['r_y'].append((mat[0][2]-mat[2][0])/(4*r_w))
            rtn['r_z'].append((mat[1][0]-mat[0][1])/(4*r_w))

            # Computes elapsed time to sleep according to selected frequency
            sleep_time = interval - (time.time()-start)
            if sleep_time > 0:
                time.sleep(sleep_time)
        return rtn

    def get_pose(self, target_device_key, ref_device_key=None):
        """Retrieve selected pose from openvr.

        :param target_device_key: the key of target device (default None)
        :param ref_device_key: the key of reference device (relative result)

        :type target_device_key: str
        :type ref_device_key: str

        :returns: transformation matrix
        :rtype: numpy (4,4) ndarray
        """
        poses = self.vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)

        target_id = self.devices[target_device_key]['index']
        if ref_device_key is None:
            return np.concatenate((
                poses[target_id].mDeviceToAbsoluteTracking.m,
                [[0, 0, 0, 1]]))
        else:
            ref_id = self.devices[ref_device_key]['index']
            target_transform = Transform(np.concatenate((
                poses[target_id].mDeviceToAbsoluteTracking.m,
                [[0, 0, 0, 1]])))
            ref_transform = Transform(np.concatenate((
                poses[ref_id].mDeviceToAbsoluteTracking.m,
                [[0, 0, 0, 1]])))
            return target_transform.relative_transform(ref_transform).matrix

    def get_poses(self, ref_device_key=None):
        """Retrieve all poses from openvr.

        :param target_device_key: the key of target device (default None)

        :type ref_device_key: str

        :returns: dict with all transfomration matrices
        :rtype:  python dict
        """
        poses = self.vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)
        return_dict = {}
        if ref_device_key is None:
            for device in self.devices:
                target_id = self.devices[device]['index']
                return_dict[device] = np.concatenate((
                        poses[target_id].mDeviceToAbsoluteTracking.m,
                        [[0, 0, 0, 1]]))
        else:
            for device in self.devices:
                if not device == ref_device_key:
                    target_id = self.devices[device]['index']
                    ref_id = self.devices[ref_device_key]['index']
                    target_transform = Transform(np.concatenate((
                        poses[target_id].mDeviceToAbsoluteTracking.m,
                        [[0, 0, 0, 1]])))
                    ref_transform = Transform(np.concatenate((
                        poses[ref_id].mDeviceToAbsoluteTracking.m,
                        [[0, 0, 0, 1]])))
                    return_dict[device] = target_transform.relative_transform(
                        ref_transform).matrix
        return return_dict

    def get_corrected_poses(self, ref_device_key=None):
        """Retrieve all poses from openvr in right hand convention.

        :param target_device_key: the key of target device (default None)

        :type ref_device_key: str

        :returns: dict with all transfomration matrices
        :rtype:  python dict
        """
        poses = self.vr.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseStanding, 0,
            openvr.k_unMaxTrackedDeviceCount)
        return_dict = {}
        if ref_device_key is None:
            for device in self.devices:
                target_id = self.devices[device]['index']
                return_dict[device] = self.correct_transformation_matrix(
                    np.concatenate((
                        poses[target_id].mDeviceToAbsoluteTracking.m,
                        [[0, 0, 0, 1]])))
        else:
            for device in self.devices:
                if not device == ref_device_key:
                    target_id = self.devices[device]['index']
                    ref_id = self.devices[ref_device_key]['index']
                    target_transform = Transform(np.concatenate((
                        poses[target_id].mDeviceToAbsoluteTracking.m,
                        [[0, 0, 0, 1]])))
                    ref_transform = Transform(np.concatenate((
                        poses[ref_id].mDeviceToAbsoluteTracking.m,
                        [[0, 0, 0, 1]])))
                    return_dict[device] = self.correct_transformation_matrix(
                        target_transform.relative_transform(
                            ref_transform).matrix)
        return return_dict

    def get_devices_count(self, type=None):
        """Count devices of one type if selected, otherwise all devices.

        :param type: the filtering type
        :type type: str

        :returns: cound of devices of selected type
        :rtype: int
        """
        if type is None:
            return len(self.devices)
        else:
            return sum(
                device['type'] == type for device in self.devices.values())
