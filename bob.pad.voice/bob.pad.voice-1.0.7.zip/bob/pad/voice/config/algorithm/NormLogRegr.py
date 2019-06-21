
import bob.pad.voice

algorithm = bob.pad.voice.algorithm.LogRegr(
    # use PCA to reduce dimension of features
    use_PCA_training = False,
    normalize_features = True,
)

