"""
In this problem, we will learn about a simple algorithm for removing noise from ('denoising')
an image. We will want to use vectorization to write an efficient algorithm for this.
"""

from typing import *
from numpy import ndarray

import numpy as np

__all__ = ["grader1", "grader2", "grader3"]


def print_passed(hash_str: str):
    msg = f"""
============================== ALL TESTS PASSED! ===============================
                                  Great Job!
================================================================================
"""
    print(msg)


def grader1(student_func: Callable[[ndarray], ndarray]):
    """ Grades Problem 1: local energy of each pixel """

    from bwsi_grader import compare_functions
    print("Please note that these problem are *not* graded. The autograder "
          "will tell you if your solution is correct, but will not provide a hash."
          "The solution notebook is available on EdX.")

    def soln(img):
        ''' Given a 2D array of color values, produces a 2D array with
            the energy at each pixel, where energy is defined as the sum
            of each's pixels neighbors differing in color from that pixel.

            Parameters
            ----------
            img : numpy.ndarray, shape=(M, N)
                An MxN array of color values.

            Returns
            -------
            numpy.ndarray, shape=(M, N)
                An MxN array of energy values.
        '''
        energies = np.zeros_like(img)

        energies[:-1] += img[:-1] != img[1:]           # below
        energies[1:] += img[1:] != img[:-1]            # above
        energies[:, :-1] += img[:, :-1] != img[:, 1:]  # right
        energies[:, 1:] += img[:, 1:] != img[:, :-1]   # left

        return energies

    # check standard case
    img = np.array([[0, 0, 0, 0, 1, 1, 0, 1],
                    [0, 1, 0, 0, 1, 1, 1, 1],
                    [0, 0, 0, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 1, 1, 1, 1],
                    [0, 0, 1, 0, 1, 1, 1, 1]])
    compare_functions(student=student_func, soln=soln, fn_args=(img,))

    # check random cases
    for i in range(100):
        shape = np.random.randint(3, 7, 2)
        img = np.random.randint(0, 255, size=shape).astype('uint8')
        compare_functions(student=student_func, soln=soln, fn_args=(img,))

    print_passed("Great job!" + "!"*46)


def grader2(student_func: Callable[[ndarray, Tuple[int, int]], List[int]]):
    """ Grades Problem 2: neighbor colors."""

    from bwsi_grader import compare_functions


    def soln(img, pixel):
        ''' Given a 2D array of color values and the position of a pixel,
            returns a list of `pixel`'s neighboring color values.

        Parameters
        ----------
        img : numpy.ndarray, shape=(M, N)
            An MxN array of color values
        pixel : tuple[int, int]
            The (r, c) index of the pixel whose neighbors to retrieve.

        Returns
        -------
        List[int]
            The color (or label) value of each of `pixel`'s neighbors.
        '''
        neighbor_vals = []
        if pixel[0] > 0:
            neighbor_vals.append(img[pixel[0]-1, pixel[1]])
        if pixel[1] > 0:
            neighbor_vals.append(img[pixel[0], pixel[1]-1])
        if pixel[0] < img.shape[0]-1:
            neighbor_vals.append(img[pixel[0]+1, pixel[1]])
        if pixel[1] < img.shape[1]-1:
            neighbor_vals.append(img[pixel[0], pixel[1]+1])
        return neighbor_vals


    # check std case
    img = np.ones((3, 3))
    pixel = (1, 1)

    compare_functions(student=student_func, soln=soln, fn_args=(img, pixel))

    # check random cases
    for i in range(100):
        rand_shape = tuple(np.random.randint(3, 7, 2))
        rand_r = np.random.randint(rand_shape[0]-1)
        rand_c = np.random.randint(rand_shape[1]-1)
        img = np.random.randint(0, 255, rand_shape)
        pixel = (rand_r, rand_c)
        compare_functions(student=student_func, soln=soln, fn_args=(img, pixel))

    print_passed("Great job!" + "!"*46)


def grader3(student_func: Callable[[ndarray], ndarray]):
    """ Grades Problem 3: Iterated Conditional Modes"""

    from bwsi_grader import compare_functions

    def soln(img):
        img = img.copy()

        def compute_energy(img):
            energies = np.zeros_like(img)
            energies[:-1] += img[:-1] != img[1:]           # below
            energies[1:] += img[1:] != img[:-1]            # above
            energies[:, :-1] += img[:, :-1] != img[:, 1:]  # right
            energies[:, 1:] += img[:, 1:] != img[:, :-1]   # left
            return energies

        def get_neighbor_colors(img, pixel):
            neighbor_vals = []
            if pixel[0] > 0:
                neighbor_vals.append(img[pixel[0]-1, pixel[1]])
            if pixel[1] > 0:
                neighbor_vals.append(img[pixel[0], pixel[1]-1])
            if pixel[0] < img.shape[0]-1:
                neighbor_vals.append(img[pixel[0]+1, pixel[1]])
            if pixel[1] < img.shape[1]-1:
                neighbor_vals.append(img[pixel[0], pixel[1]+1])
            return neighbor_vals

        energies = compute_energy(img)
        highest_energy = np.divmod(np.argmax(energies), img.shape[1])
        neighbors = get_neighbor_colors(img, highest_energy)
        (neighbor_labels, neighbor_counts) = np.unique(neighbors, return_counts=True)
        best_label = neighbor_labels[np.argmax(neighbor_counts)]
        img[highest_energy] = best_label
        return img

    # check standard case
    img = np.array([[0, 0, 0, 0, 1, 1, 0, 1],
                    [0, 1, 0, 0, 1, 1, 1, 1],
                    [0, 0, 0, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 1, 1, 1, 1],
                    [0, 0, 1, 0, 1, 1, 1, 1]])
    compare_functions(student=student_func, soln=soln, fn_args=(img,))

    # check random cases
    for i in range(100):
        shape = np.random.randint(3, 7, 2)
        img = np.random.randint(0, 255, size=shape).astype('uint8')
        compare_functions(student=student_func, soln=soln, fn_args=(img,))

    print_passed("Great job!" + "!"*46)
