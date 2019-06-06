# This is the class file for an individual in the population.
# The genes of the individual are passed in when the GA is created

class Individual:
    """
    This class defines a single individual in the population

    :Parameters:
        **genes: dictionary**

        The dictionary is indexed by the gene name, and the corresponding value is the gene value.

        Example:

        =====  ===  ===
        =====  ===  ===
        gene    x    y

        value  3.2  1.7
        =====  ===  ===

        This gene would be represented as the following dictionary:

         .. code-block:: python

            genes = {'x': 3.2, 'y': 1.7}

    :attributes:

        **fitness_score: float**

            The fitness is calculated from the genes by ``evaluate()``

        **data: dictionary**

            This is where you can store additional data. Assignment should be done in the ``evaluate()`` function passed to the ga class.


    """

    def __init__(self, genes):

        self.data = {}
        self.genes = self.validate(genes)
        self.evaluate()


