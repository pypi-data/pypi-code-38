import sys
import numpy as np
from gaga.Individual import Individual
from gaga.Results import Results
import pickle
import bz2
import os


class ga:
    """
    This is the genetic algorithm class.

    :Parameters:

        **gene_definition: dictionary**
            Defines the name of each gene and its initial bounds.

            Example:

            *x*, :math:`0<x<1`

            *y*, :math:`0<y<2`

            .. code-block:: python

                gene_definition = {'x': (0, 1), 'y': (0, 2)}

        **evaluate: function**

    :Optional parameters:

        **results_folder: string, (default = 'results')**
            Path to where all results files will be saved

        **problem_type: string, (default = 'minimise')**
            Specify whether the goal is to minimise or maximise the fitness score (i.e. the objective function)

        **population_size: int, (default = 100)**
            The number of individuals that make up the initial population. Also the number of individuals in each generation.

        **epoch: int, (default = 100)**
            The number of iterations the simulation runs for. i.e. the number of generations produced.

        **clone: int, (default = 1)**
            The number of the best individuals kept for each generation. By default, this clones the best individual of the current generation so that it will live in the next generation.

        **mutate: int, float, (default = 0.3)**
            The number of individuals in the next generation that will be created by mutating the current generation.

            * if int, this will be the number of mutants

            * if float, this will be the percentage of the population that will be mutants but rounded up.

                Example:

                If ``population_size = 25`` and ``mutate = 0.1`` then in each generation, there will be 3 mutants.

        **selection: string, (default = 'tournament')**
            Specifies the method of selection. Choose from: 'tournament', 'roulette_wheel'.

            .. seealso::

                :ref:`selection <selection-theory>`

            * .. automethod:: _ga__tournament

            * .. automethod:: _ga__roulette_wheel

        **winrate: float, (default = 0.7)**
            Only used for ``_ga__tournament()``.

            Specifies the probability that the individual with the better fitness score will 'win the tournament' and be selected for the gene pool.

        **crossover: string, (default = 'multiUniform')**
            Specifies the method of crossover. Choose from: 'multi_uniform', 'brood', 'arithmetic'
            
            * .. automethod:: _ga__multi_uniform

            * .. automethod:: _ga__brood

            * .. automethod:: _ga__arithmetic

        **mutation: string, (default = 'gaussian')**

        **sigma float, (default = 0.1)**

        **verbose: boolean, (default = False)**

        **mutate_crossover: boolean, (default = False)**
            Specifies the method of mutation. Choose from: 'gaussian', 'random'

            * .. automethod:: _ga__gaussian_mutation

            * .. automethod:: _ga__random_mutation

        **speciate: boolean, (default = False)**

        **logspaced: list, (default = [])**

        **load: boolean (default = False)**


    """

    def __init__(self, gene_definition, evaluate,
                 results_folder = "results",
                 problem_type = "minimise",
                 population_size = 100,
                 epoch = 100,
                 clone = 1,
                 mutate = 0.3,
                 selection = "tournament",
                 crossover = "multi_uniform",
                 mutation = "gaussian",
                 sigma = 0.1,
                 winrate = 0.7,
                 verbose = False,
                 mutate_crossover = False,
                 cross_scale = 0.01,
                 speciate = False,
                 logspaced = [],
                 load = False):

        # Gene constants
        self.n_genes = len(gene_definition.items())
        self.gene_names = list(gene_definition.keys())
        self.lower_bounds = {i: gene_definition[i][0] for i in self.gene_names}
        self.upper_bounds = {i: gene_definition[i][1] for i in self.gene_names}
        self.logspaced = logspaced

        # Simulation constants
        self.problem_type = problem_type
        self.reverse = self.problem_type == "maximise"
        self.population_size = population_size

        self.n_clone = clone    # percentage of the new generation produced by cloning

        if isinstance(mutate, int):
            self.n_mutate = mutate
        else:
            self.n_mutate = int(np.ceil(mutate*population_size))   # percentage of the new generation produced by mutation

        self.n_crossover = self.population_size - self.n_clone - self.n_mutate # number produced by crossover

        if self.n_crossover < 0:
            sys.exit("""...
ERROR in settings.
The clone and mutant rates are too high. No individuals produced by crossover.
Reduce either the clone or mutant rate (or both).
...""")

        self.gene_poolN = 2 * self.n_crossover

        # Functions
        self.selection = self.__tournament
        if selection == "roulette_wheel":
            self.selection = self.__roulette_wheel

        self.crossover = self.__multi_uniform
        if crossover == "brood":
            self.crossover = self.__brood
        if crossover == "arithmetic":
            self.crossover = self.__arithmetic

        self.mutation = self.__gaussian_mutation
        self.sigma = sigma

        if mutation == "random":
            self.mutation = self.__random_mutation

        # Assign constants to the Individual class
        Individual.gene_names = self.gene_names
        Individual.lower_bounds = self.lower_bounds
        Individual.upper_bounds = self.upper_bounds
        Individual.evaluate = evaluate
        Individual.validate = self.__validate_chromosome

        # Hyper parameters
        self.winRate = winrate
        self.epoch = epoch # termination condition
        self.verbose = verbose # prints out population details at each epoch

        self.mutate_crossover = mutate_crossover
        self.cross_scale = cross_scale
        self.speciate = speciate

        self.results_folder = results_folder + '/'
        self.results = Results()
        self.results.gene_names = self.gene_names
        self.results.results_folder = self.results_folder


        if not os.path.exists(self.results_folder):
            os.makedirs(self.results_folder)

        # Name of the folder of the simulation we want to continue from
        # Otherwise False
        self.history_folder = load


        # Keep a record of the previous simulations
        if load == False:
            with open(self.results_folder + "history.txt", 'w') as f:
                f.write(self.results_folder)
        else:
            with open(self.history_folder + "history.txt", 'r') as f:
                hist = f.read()
            with open(self.results_folder + "history.txt", 'w') as f:
                f.write(hist)
                f.write(self.results_folder)

        # with bz2.BZ2File(self.results_folder + "settings_obj", 'wb') as f:
        #     pickle.dump(settings, f)

    def info(self):
        """This function will display simulation information

        """
        print("")
        print("Results_folder{}".format(self.results_folder))

        print("This function hasn't been written yet")

    def run_simulation(self, seed = 0):

        ''' Forced to actually run a simulation'''
        np.random.seed(seed)

        self.__init_population()
        for i in range(self.epoch):

            if self.verbose:
                self.__print_ind(self.new_population, title="epoch: " + str(i))
            self.__save_results(i)

            self.__refresh()
            self.selection()
            if self.speciate:
                self.__order_gene_pool(i)
            # Create a new population and populate with crossover, mutation and cloning
            self.new_population = []
            self.crossover()
            # self.__print_ind(self.new_population, title="New population (after crossover)")
            self.__clone()
            # self.__print_ind(self.new_population, title="New population (after cloning)")
            self.mutation()
        if self.verbose:
            self.__print_ind(self.new_population, title="final population")
        self.__save_results(self.epoch)


    def measure_diversity(self):
         # coefficient of variation (relative standard deviation)
        div = {}
        for gene in self.gene_names:
            # all the values of a particular gene in the population
            vals = [ind.genes[gene] for ind in self.new_population]
            div[gene] = np.std(vals)/abs(np.mean(vals))

        self.diversity = div
        self.average_diversity = np.mean(list(div.values()))

    def __tune_hyper_parameters(self):
        ''' Tune the hyper-parameters based on the diversity of the population'''
        pass

    def __random_sample_logspace(self, start, end):
        sample = np.random.uniform(np.log(start), np.log(end))
        return np.exp(sample)

    def __init_population(self):

        ''' Create an initial population within the specified bounds '''

        # Start with a random population
        if self.history_folder == False:
            # Create a random set of chromosomes
            init_chromosomes = []
            for individual in range(self.population_size):
                # create a random chromosome
                chromosome = {}
                for gene in self.gene_names:
                    if gene in self.logspaced:
                        chromosome[gene] = self.__random_sample_logspace(self.lower_bounds[gene], self.upper_bounds[gene])
                    else:
                        chromosome[gene] = np.random.uniform(self.lower_bounds[gene], self.upper_bounds[gene])
                init_chromosomes.append(chromosome)

            # Create individuals
            self.new_population = [Individual(chromosome) for chromosome in init_chromosomes]
        else:
            with bz2.BZ2File(self.history_folder + "results_obj", 'rb') as f:
                results = pickle.load(f)
                self.new_population = results.data["history"][-1]

    def __refresh(self):
        ''' Refreshes the world after each epoch'''
        self.population = self.new_population
        self.new_population = []

#   selection
#   Each selection method creates self.gene_pool through selection from self.population which
#   is a list of individuals that will go on to reproduce. The number of individuals is
#   specified by self.gene_poolN

    def __tournament(self):
        ''' Tournament selection. Two individuals are selected to enter into the tournament.
		The individual with the higher fitness score has a win rate chance of winning the tournament, while the individual with the lower fitness score has a (1 - win rate) chance of winning tournament. The tournament winner goes into the gene pool
		'''

        self.gene_pool = []  # create an empty gene pool

        # 	each tournament adds one individual to the gene pool
        for tournament in range(self.gene_poolN):
            participants = np.random.choice(self.population, size = 2, replace = False)

            # sort participants by rank
            participants = sorted(participants, key = lambda individual: individual.fitness_score, reverse = self.reverse)

            if np.random.uniform() < self.winRate:
                winner = participants[0]
            else:
                winner = participants[1]

            self.gene_pool.append(winner)

    def __roulette_wheel(self):
        '''Individuals are selected by spinning a roulette wheel. Each slice on the wheel represents an individual. The area of the slice corresponds to their fitness score.'''

        max_fitness = max([ind.fitness_score for ind in self.population])

        inv_fitness = [max_fitness -  ind.fitness_score + 1 for ind in self.population]

        cd = [sum(inv_fitness[:(i+1)]) for i in range(len(inv_fitness))]
        cd = np.asarray(cd)

        ind_selection = [sum(cd < cd[-1]*np.random.random()) for i in range(self.gene_poolN)]

        self.gene_pool = [self.population[i] for i in ind_selection]

#   crossover
#   Each crossover method uses individuals from self.gene_pool and adds self.n_crossover individuals to self.new_population.
#   Note: self.gene_poolN is always even

    def __order_gene_pool(self, epoch):

        # select gene:
        gene_order = self.gene_names[epoch % len(self.gene_names)]
        self.gene_pool.sort(key = lambda ind: ind.genes[gene_order])

    def __arithmetic(self):
        r = np.random.uniform()
        for pair in range(0, 2*self.n_crossover, 2):
            mother = self.gene_pool[pair]
            father = self.gene_pool[pair + 1]

            chromosome = {}
            for gene in self.gene_names:
                chromosome[gene] = r * mother.genes[gene] + (1-r) * father.genes[gene]

            # create individuals
            child = Individual(chromosome)

            # take the best child and add it to the next generation
            self.new_population.append(child)

    def __multi_uniform(self):
        '''This creates 1 child using the mask. The mask created is uniformly and randomly chosen.'''

        offspring = []

        for pair in range(0, 2*self.n_crossover, 2):
            mother = self.gene_pool[pair]
            father = self.gene_pool[pair + 1]

            # size: no. of parameters it picks. At least 1 gene, but less than self.n_genes parameters
            # chooses randomly without replacement which parameters to put in the mask
            mask = np.random.choice(self.gene_names, size = np.random.randint(1, self.n_genes), replace = False)

            chromosome = {}
            for gene in self.gene_names:
                if gene in mask:
                    chromosome[gene] = mother.genes[gene]
                else:
                    chromosome[gene] = father.genes[gene]

            if self.mutate_crossover:
                g = np.random.choice(self.gene_names)
                chromosome[g] = np.random.normal(loc = chromosome[g], scale = abs(self.cross_scale * chromosome[g]))

            # create individuals
            child = Individual(chromosome)

            # take the best child and add it to the next generation
            self.new_population.append(child)

    def __brood(self):
        '''This creates 2 children using the mask and the inverse mask. We then take the best child. The mask created is uniformly and randomly chosen.'''

        offspring = []

        for pair in range(0, 2*self.n_crossover, 2):
            mother = self.gene_pool[pair]
            father = self.gene_pool[pair + 1]

            # size: no. of parameters it picks. At least 1 gene, but less than self.n_genes parameters
            # chooses randomly without replacement which parameters to put in the mask
            mask = np.random.choice(self.gene_names, size = np.random.randint(1, self.n_genes), replace = False)

            chromosome_1 = {}
            chromosome_2 = {}
            for gene in self.gene_names:
                if gene in mask:
                    chromosome_1[gene] = mother.genes[gene]
                    chromosome_2[gene] = father.genes[gene]
                else:
                    chromosome_1[gene] = father.genes[gene]
                    chromosome_2[gene] = mother.genes[gene]

            if self.mutate_crossover:
                for gene in self.gene_names:
                    chromosome_1[gene] = np.random.normal(loc = chromosome_1[gene], scale = self.cross_scale * chromosome_1[gene])
                    chromosome_2[gene] = np.random.normal(loc=chromosome_2[gene], scale=self.cross_scale * chromosome_2[gene])

            if self.mutate_crossover:
                g1 = np.random.choice(self.gene_names)
                chromosome_1[g1] = np.random.normal(loc = chromosome_1[g1], scale = abs(self.cross_scale * chromosome_1[g1]))
                g2 = np.random.choice(self.gene_names)
                chromosome_2[g2] = np.random.normal(loc=chromosome_2[g2], scale=abs(self.cross_scale * chromosome_2[g2]))

            # create individuals
            child_1 = Individual(chromosome_1)
            child_2 = Individual(chromosome_2)

            children = sorted([child_1, child_2], key = lambda individual: individual.fitness_score, reverse = self.reverse)

            # take the best child and add it to the next generation
            self.new_population.append(children[0])

#   MUTATE
    def __random_mutation(self):
        ''' This is the random mutation function described in Tang, Tseng, 2012 '''

        # Select individuals from the previous population to mutate. an individual can only be selected once
        to_mutate = np.random.choice(self.population, size = self.n_mutate, replace = False)

        # Work out the maximum and minimum value of each parameter
        # A matrix where each row are the genes of an individual
        gene_max = {gene: max([i.genes[gene] for i in self.population]) for gene in self.gene_names}
        gene_min = {gene: min([i.genes[gene] for i in self.population]) for gene in self.gene_names}

        for ind in to_mutate:
            chr = ind.genes # original chromosome
            delta = {gene: max(2 * (chr[gene] - gene_min[gene]), 2 * (gene_max[gene] - chr[gene])) for gene in self.gene_names}
            new_chr = {gene: chr[gene] + delta[gene] * (np.random.uniform(0,1) - 0.5) for gene in self.gene_names}
            mutant = Individual(new_chr)
            self.new_population.append(mutant)

    def __gaussian_mutation(self, replace = False):

        to_mutate = np.random.choice(self.population, size=self.n_mutate, replace=False)

        for ind in to_mutate:
            chr = ind.genes
            chr_copy = {k:v for k, v in chr.items()}

            # pick a gene to mutate
            g = np.random.choice(self.gene_names)
            chr_copy[g] = min(max(np.random.normal(loc = chr_copy[g], scale = self.sigma), self.lower_bounds[g]), self.upper_bounds[g])
            mutant = Individual(chr_copy)

            self.new_population.append(mutant)


    def __clone(self):

        # rank the previous population
        ranked = sorted(self.population, key = lambda individual: individual.fitness_score, reverse = self.reverse)

        for i in range(self.n_clone):
            self.new_population.append(ranked[i])

    # PRINTING

    def __print_ind(self, list_ind, dp = ".4f", title = None):
        ''' Convenience function. Pass in a list of individuals and it will print out the chromosomes and the fitness score'''
        if title:
            print("=" * len(title))
            print(title.upper())

        data = [[i.fitness_score] + [i.genes[gene] for gene in self.gene_names] for i in list_ind]

        # print(tabulate(data, headers = ["Fitness Score"] + self.gene_names, tablefmt = "rst", floatfmt = dp))
        for i in data:
            print(i)

    def __save_results(self, epoch):
        '''save results at each epoch'''
        self.measure_diversity()

        self.results.data["history"].append(self.new_population)
        self.results.data["fitness"].append([i.fitness_score for i in self.new_population])
        self.results.data["genes"].append({gene: [i.genes[gene] for i in self.new_population] for gene in self.gene_names})
        self.results.data["diversity"].append(self.diversity)
        self.results.data["average_diversity"].append(self.average_diversity)

        # data saved at the end of the evaluation function
        eval_data = self.new_population[0].data.keys()

        for i in eval_data:
            if i not in self.results.data:
                self.results.data[i] = []

        for j in eval_data:
            self.results.data[j].append([i.data[j] for i in self.new_population])

        self.results.epochs += 1

        with bz2.BZ2File(self.results_folder + "results_obj", 'wb') as f:
            pickle.dump(self.results, f)

    # genes VALIDATION
    def __validate_chromosome(self, chromosome):
        ''' Ensure that a chromosome is valid. If invalid, returns a new valid chromosome. '''

        # keep chromosome within initial bounds
        for gene in self.gene_names:
            lb = self.lower_bounds[gene]
            ub = self.upper_bounds[gene]
            chromosome[gene] = min(chromosome[gene], ub)
            chromosome[gene] = max(chromosome[gene], lb)

        return chromosome
