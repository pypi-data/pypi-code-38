import numpy
import random

class BinaryGA():
    def __init__(self,
    genes,
    generation_size,
    number_of_generations,
    mutation_probability,
    genom_size_penalization=0,
    fintess_calculation=None,
    population_fitness_calculation=None,
    continuous_export: bool=True,
    file_name: str="generations.json"
    ):
        self.genes = genes
        self.number_of_genes = len(genes)
        self.generation_size = generation_size
        self.number_of_generations = number_of_generations
        self.mutation_probability = mutation_probability
        self.genom_size_penalization = genom_size_penalization
        self.continuous_export = continuous_export
        self.file_name = file_name
        self.generation_history = []

        if(fintess_calculation == None):
            self.fintess_calculation = self.default_fintess_calculation
        else:
            self.fintess_calculation = fintess_calculation

        if(population_fitness_calculation == None):
            self.population_fitness_calculation = self.default_population_fintess_calculation
        else:
            self.population_fitness_calculation = population_fitness_calculation

    def run(self):
        pop_size = (self.generation_size, self.number_of_genes)
        new_population = numpy.random.choice(2, pop_size)
        self.generation_history = []

        for generation in range(self.number_of_generations):
            print("Starting generation: " + str(generation))
            # Measuring the fitness of each chromosome in the population.
            fitness = self.population_fitness_calculation(self.genes, new_population)
            penalized_fitness = self.penalize_fitness(fitness, new_population)

            self.log_generation_history(new_population, penalized_fitness, generation)
            
            # Selecting the best parents in the population for mating.
            parents = self.select_mating_pool(new_population, penalized_fitness)

            if(self.all_parents_same(parents)):
                print("All parents are same. Stopping evalution.")
                return (self.select_best_genom(self.generation_history), self.generation_history)

            # Generating next generation using crossover.
            offspring_crossover = self.crossover(parents,
                                                 offspring_size=(pop_size[0]-parents.shape[0], self.number_of_genes))

            # Adding some variations to the offsrping using mutation.
            offspring_mutation = self.mutation(
                offspring_crossover, self.mutation_probability)
            # Creating the new population based on the parents and offspring.
            new_population[0:parents.shape[0], :] = parents
            new_population[parents.shape[0]:, :] = offspring_mutation

        return (self.select_best_genom(self.generation_history), self.generation_history)

    def penalize_fitness(self, fitness, population):
        penalized_fitnesses = []

        for index in range(len(fitness)):
            genom = population[index]
            selected_genes = numpy.where(genom == 1)[0]
            num_selected_genes = len(selected_genes)
            penalization = num_selected_genes * self.genom_size_penalization
            penalized_fitness = fitness[index] - penalization

            penalized_fitnesses.append((fitness[index], penalized_fitness))

        return penalized_fitnesses
    def log_generation_history(self,  population, population_fintess:list, generation_index:int):
        generation_records = self.get_generation_record(population, population_fintess, generation_index)
        self.generation_history = self.generation_history + generation_records

        if(self.continuous_export):
            file = open(self.file_name, "w")
            file.write("[")

            isFirst = True

            for generation in self.generation_history:
                if(isFirst):
                    file.write(generation.print())
                    isFirst = False
                else:
                    file.write("," + generation.print())

            file.write("]")
            file.close()
    
    def all_parents_same(self, parents):
        compare = parents[0]
        for parent in parents:
            if(not numpy.array_equal(parent, compare)):
                return False
        return True        

    def select_best_genom(self, generation_history):
        best_record = generation_history[0]

        for record in generation_history:
            if(record.penalized_fitness > best_record.penalized_fitness):
                best_record = record
        
        return best_record
    
    def get_generation_record(self, population, population_fintess, generation_index):
        generation_records = []

        for index in range(len(population_fintess)):
            fitness = population_fintess[index]
            genom = population[index]
            selected_genes = BinaryGA.get_selected_genes(self.genes, genom)
            record = GenerationRecord(selected_genes, genom, fitness[0], fitness[1], generation_index)
            generation_records.append(record)

        return generation_records

    def default_population_fintess_calculation(self, genes, pop):
        fitnesses = []

        for genom in pop:
            selected_genes = BinaryGA.get_selected_genes(genes, genom)
            fintess = self.fintess_calculation(selected_genes, genom)

            fitnesses.append(fintess)

        return fitnesses

    def default_fintess_calculation(self, selected_genes, genom):
        fitness = 0
        for gene in selected_genes:
            fitness += gene
        
        return fitness

    @staticmethod
    def get_selected_genes(genes, genom):
        selected_genes = []
        index = 0

        for gene in genes:
            if genom[index] == 1:
                selected_genes.append(gene)
            index += 1
        return selected_genes

    def select_mating_pool(self, pop, fitness):
        num_parents = int(self.generation_size/2)
        # Selecting the best individuals in the current generation as parents for producing the offspring of the next generation.
        parents = numpy.empty((num_parents, pop.shape[1]))
        fitness_copy = []
        for fit in fitness:
            fitness_copy.append(fit[1])

        for parent_num in range(num_parents):
            max_fitness_idx = numpy.where(fitness_copy == numpy.max(fitness_copy))
            max_fitness_idx = max_fitness_idx[0][0]
            parents[parent_num, :] = pop[max_fitness_idx, :]
            fitness_copy[max_fitness_idx] = -99999999999

        return parents

    def crossover(self, parents, offspring_size):
        offspring = numpy.empty(offspring_size)
        # The point at which crossover takes place between two parents. Usually, it is at the center.
        

        for k in range(offspring_size[0]):
            crossover_point = random.randint(0, self.number_of_genes - 1)

            # Index of the first parent to mate.
            parent1_idx = k % parents.shape[0]
            # Index of the second parent to mate.
            parent2_idx = (k+1) % parents.shape[0]
            # The new offspring will have its first half of its genes taken from the first parent.
            offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
            # The new offspring will have its second half of its genes taken from the second parent.
            offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
        return offspring

    def mutation(self, offspring_crossover, mutation_probability):
        # Mutation changes a single gene in each offspring randomly.
        for offspring_index in range(offspring_crossover.shape[0]):
            for gene_index in range(offspring_crossover.shape[1]):
                if(self.should_mutate(mutation_probability)):
                    if(offspring_crossover[offspring_index][gene_index] == 1):
                        offspring_crossover[offspring_index][gene_index] = 0
                    else:
                        offspring_crossover[offspring_index][gene_index] = 1

        # for idx in range(offspring_crossover.shape[0]):
        #      # The random value to be added to the gene.
        #      random_value = numpy.random.uniform(-1.0, 1.0, 1)
        #      offspring_crossover[idx, 4] = offspring_crossover[idx, 4] + random_value

        return offspring_crossover

    def should_mutate(self, mutation_probability):
        return random.randint(0, 99) < (mutation_probability * 100)

import json
class GenerationRecord:
    def __init__(self, genes, genom:list, fitness, penalized_fitness, generation_index, dic = None):
        self.fitness = fitness
        self.penalized_fitness = penalized_fitness
        self.generation_index = generation_index
        self.genes = genes
        self.genom = list(map(int, list(genom)))

        if(dic != None):
            self.__dict__ = dic

    def print(self):
        return json.dumps(self.__dict__)


    

