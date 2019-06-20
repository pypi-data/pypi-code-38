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

    # Dimensionality (1D,2D,3D, etc. - all dims are supported, but only 1D will be possible to plot pairs and probability)
    dim = 2

    # Number of particles
    N = 1000

    # Positions
    posns = np.random.normal(0.0,10.0, size=(N,dim))

    # Setup the sampler

    # Cutoff counting probabilities for particles that are more than:
    # std_dev_clip_mult * std_dev
    # away from each-other
    std_dev = 1.0
    std_dev_clip_mult = 3.0

    # Make the probability calculator
    prob_calculator = ProbCalculator(posns,std_dev,std_dev_clip_mult)
    # Distances have already been computed for us between all particles

    # Make the sampler
    sampler = Sampler(prob_calculator)

    # Sample many particle pairs

    # Handle failure
    def handle_fail(ith_particle):
        print("Could not draw the " + str(ith_particle) + " particle: try adjusting the std. dev. for the probability cutoff.")
        sys.exit(0)

    # For efficiency, just compute the first particle probability now
    prob_calculator.compute_un_probs_first_particle()
    compute_un_probs_first_particle = False

    no_samples = 10000
    no_tries_max = 100
    idxs_1 = []
    idxs_2 = []
    for i in range(0,no_samples):

        # Sample using rejection sampling
        success = sampler.rejection_sample_pair(no_tries_max,compute_un_probs_first_particle)
        if not success:
            handle_fail(i)

        # Alternatively sample using CDF
        # sampler.cdf_sample_first_particle()
        # sampler.cdf_sample_second_particle()

        # Append
        idxs_1.append(sampler.idx_first_particle)
        idxs_2.append(sampler.idx_second_particle)

    # For each idx, get distances
    dists = {}
    for i in range(0,no_samples):
        idx1 = idxs_1[i]
        idx2 = idxs_2[i]
        pos1 = posns[idx1]
        pos2 = posns[idx2]
        dist = np.sqrt(sum(pow(pos1-pos2,2)))
        if idx1 in dists:
            dists[idx1].append(dist)
        else:
            dists[idx1] = [dist]
        if idx2 in dists:
            dists[idx2].append(dist)
        else:
            dists[idx2] = [dist]

    # Average dist
    ave_dist = np.full(N,0.0)
    for idx, dist in dists.items():
        ave_dist[idx] = np.mean(dist)

    # Counts
    counts = np.full(N,0).astype(int)
    for idx, dist in dists.items():
        counts[idx] = len(dist)

    # Plot
    plt.figure()
    min_dist = min(ave_dist)
    max_dist = max(ave_dist-min_dist)
    cols = [str((dist-min_dist) / max_dist) for dist in ave_dist]
    plt.scatter(posns[:,0],posns[:,1], c=cols, cmap=plt.cm.jet)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(str(N)+ " particles: ave dist of other particle")

    plt.figure()
    min_count = min(counts)
    max_count = max(counts-min_count)
    cols = [str((count-min_count) / max_count) for count in counts]
    plt.scatter(posns[:,0],posns[:,1], c=cols, cmap=plt.cm.jet)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(str(N)+ " particles: counts of draws")

    # Show
    plt.show()
