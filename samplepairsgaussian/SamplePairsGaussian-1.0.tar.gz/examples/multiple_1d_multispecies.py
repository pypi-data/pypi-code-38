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
    N = 100

    # Positions of two species
    posns_A = (np.random.random(size=(N,dim))-0.5) * (2.0 * L)
    posns_B = (np.random.random(size=(N,dim))-0.5) * (2.0 * L)

    # Setup the sampler

    # Cutoff counting probabilities for particles that are more than:
    # std_dev_clip_mult * std_dev
    # away from each-other
    std_dev = 10.0
    std_dev_clip_mult = 3.0

    # Make the probability calculator
    prob_calculator_A = ProbCalculator(posns_A,std_dev,std_dev_clip_mult)
    prob_calculator_B = ProbCalculator(posns_B,std_dev,std_dev_clip_mult)
    species_arr = ["A","B"]
    prob_calculator = ProbCalculatorMultiSpecies([prob_calculator_A,prob_calculator_B],species_arr)

    # Make the sampler
    sampler = SamplerMultiSpecies(prob_calculator)
    sampler.set_logging_level(logging.INFO)

    # Sample many particle pairs

    # Handle failure
    def handle_fail():
        print("Could not draw particle: try adjusting the std. dev. for the probability cutoff.")
        sys.exit(0)

    # For efficiency, just compute the first particle probability now
    prob_calculator_A.compute_un_probs_first_particle()
    prob_calculator_B.compute_un_probs_first_particle()
    compute_un_probs_first_particle = False

    # Also compute the species probs
    prob_calculator.compute_species_probs()
    compute_species_probs = False

    no_samples = 1000
    no_tries_max = 100
    idxs_1 = {"A": [], "B": []}
    idxs_2 = {"A": [], "B": []}
    for i in range(0,no_samples):

        # Sample using rejection sampling
        success = sampler.rejection_sample_pair(no_tries_max,compute_species_probs,compute_un_probs_first_particle)
        if not success:
            handle_fail()

        # Alternatively sample using CDF
        # sampler.cdf_sample_first_particle()
        # sampler.cdf_sample_second_particle()

        # Append
        idxs_1[sampler.species_particles].append(sampler.idx_first_particle)
        idxs_2[sampler.species_particles].append(sampler.idx_second_particle)

    idxs_1["A"] = np.array(idxs_1["A"]).astype(int)
    idxs_1["B"] = np.array(idxs_1["B"]).astype(int)
    idxs_2["A"] = np.array(idxs_2["A"]).astype(int)
    idxs_2["B"] = np.array(idxs_2["B"]).astype(int)

    # Plot

    plt.figure()
    plt.hist(posns_A)
    plt.xlabel("particle position")
    plt.title("Distribution of " + str(N) + " particle positions of species A")

    plt.figure()
    plt.hist(posns_B)
    plt.xlabel("particle position")
    plt.title("Distribution of " + str(N) + " particle positions of species B")

    plt.figure()
    # Make symmetric
    idxs_1_symmetric = np.concatenate((idxs_1["A"],idxs_2["A"]))
    idxs_2_symmetric = np.concatenate((idxs_2["A"],idxs_1["A"]))
    plt.plot(posns_A[idxs_1_symmetric][:,0],posns_A[idxs_2_symmetric][:,0],'ro')
    idxs_1_symmetric = np.concatenate((idxs_1["B"],idxs_2["B"]))
    idxs_2_symmetric = np.concatenate((idxs_2["B"],idxs_1["B"]))
    plt.plot(posns_B[idxs_1_symmetric][:,0],posns_B[idxs_2_symmetric][:,0],'bo')
    plt.xlabel("position of particle #1")
    plt.ylabel("position of particle #2")
    plt.title(str(no_samples)+ " sampled pairs of particles")

    # Show
    plt.show()
