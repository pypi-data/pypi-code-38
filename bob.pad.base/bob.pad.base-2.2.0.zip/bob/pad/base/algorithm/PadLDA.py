#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import numpy
from bob.bio.base.algorithm import LDA

class PadLDA(LDA):
    """Wrapper for bob.bio.base.algorithm.LDA,

    Here, LDA is used in a PAD context. This means that the feature
    will be projected on a single dimension subspace, which acts as a score


    For more details, you may want to have a look at
    `bob.learn.linear Documentation`_

    .. _bob.learn.linear Documentation:
      https://www.idiap.ch/software/bob/docs/bob/bob.learn.linear/stable/index.html

    Attributes
    ----------
    lda_subspace_dimension : int
      the dimension of the LDA subspace. In the PAD case, the default
      value is *always* used, and corresponds to the number of classes
      in the training set (i.e. 2).
    pca_subspace_dimension : int
      The dimension of the PCA subspace to be applied
      before on the data, before applying LDA.
    use_pinv : bool
      Use the pseudo-inverse in LDA computation.

    """
    def __init__(self,
                 lda_subspace_dimension = None, # if set, the LDA subspace will be truncated to the given number of dimensions; by default it is limited to the number of classes in the training set
                 pca_subspace_dimension = None, # if set, a PCA subspace truncation is performed before applying LDA; might be integral or float
                 use_pinv = False,
                 **kwargs
                 ):
        """Init function

        Parameters
        ----------
        lda_subspace_dimension : int
          the dimension of the LDA subspace. In the PAD case, the default
          value is *always* used, and corresponds to the number of classes
          in the training set (i.e. 2).
        pca_subspace_dimension : int
          The dimension of the PCA subspace to be applied
          before on the data, before applying LDA.
        use_pinv : bool
          Use the pseudo-inverse in LDA computation.

        """
        super(PadLDA, self).__init__(
            lda_subspace_dimension = lda_subspace_dimension,
            pca_subspace_dimension = pca_subspace_dimension,
            use_pinv = use_pinv,
            **kwargs
          )

    def score(self, toscore):
        return [toscore[0]]
