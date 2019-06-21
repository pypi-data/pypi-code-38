
import bob.pad.voice

algorithm = bob.pad.voice.algorithm.GMM(
    number_of_gaussians = 512,
    kmeans_training_iterations = 10,   # Maximum number of iterations for K-Means
    gmm_training_iterations = 10,      # Maximum number of iterations for ML GMM Training
    training_threshold = 5e-5,         # Threshold to end the ML training, make it smaller
    variance_threshold = 5e-7,         # Minimum value that a variance can reach, make it smaller than default

)
