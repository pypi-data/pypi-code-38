# If installed:
from samplePairsGaussian import *

# Else: Add the path to the module
# import sys
# sys.path.append('../samplePairsGaussian/')
# from sampler import *

import sys
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":

    # Uniformly spread particles from -L to L
    L = 100

    # Dimensionality (1D,2D,3D, etc. - all dims are supported, but only 1D will be possible to plot pairs and probability)
    dim = 1

    # Number of particles
    N = 1000

    # Positions
    posns = (np.random.random(size=(N,dim))-0.5) * (2.0 * L)

    # Handle failure
    def handle_fail():
        print("Could not draw particle: try adjusting the std. dev. for the probability cutoff.")
        sys.exit(0)

    # Setup the sampler

    # Make the probability calculator
    prob_calculator = ProbCalculator(posns,0.0,0.0)
    # Distances have already been computed for us between all particles

    # Make the sampler
    sampler = Sampler(prob_calculator)

    # Func to get the samples
    def get_samples(no_samples, std_dev, std_dev_clip_mult):

        # Set the std dev and multiplier
        prob_calculator.std_dev = std_dev
        prob_calculator.std_dev_clip_mult = std_dev_clip_mult

        # For efficiency, just compute the first particle probability now
        prob_calculator.compute_un_probs_first_particle()
        compute_un_probs_first_particle = False

        no_tries_max = 100
        idxs_1 = []
        idxs_2 = []
        for i in range(0,no_samples):

            # Sample using rejection sampling
            success = sampler.rejection_sample_pair(no_tries_max,compute_un_probs_first_particle)
            if not success:
                handle_fail()

            # Alternatively sample using CDF
            # sampler.cdf_sample_first_particle()
            # sampler.cdf_sample_second_particle()

            # Append
            idxs_1.append(sampler.idx_first_particle)
            idxs_2.append(sampler.idx_second_particle)

        return [idxs_1, idxs_2]

    # Histogram of particle positions
    plt.figure()
    plt.hist(posns)
    plt.xlabel("particle position")
    plt.title("Distribution of " + str(N) + " particle positions")

    # No samples
    no_samples = 10000

    # Cutoff counting probabilities for particles that are more than:
    # std_dev_clip_mult * std_dev
    # away from each-other
    std_devs = [1.0,10.0,30.0]
    std_dev_clip_mult = 3.0
    for std_dev in std_devs:

        # Sample
        idxs_1, idxs_2 = get_samples(no_samples,std_dev,std_dev_clip_mult)

        # Plot
        plt.figure()
        idxs_1_symmetric = np.concatenate((idxs_1,idxs_2))
        idxs_2_symmetric = np.concatenate((idxs_2,idxs_1))
        plt.hist2d(posns[idxs_1_symmetric][:,0], posns[idxs_2_symmetric][:,0], bins=(20, 20), cmap=plt.cm.jet)
        plt.xlabel("position of particle #1")
        plt.ylabel("position of particle #2")
        plt.title("Std. dev. = " + str(std_dev))

    # Show
    plt.show()
