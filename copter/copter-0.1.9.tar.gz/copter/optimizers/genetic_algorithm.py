# -*- coding: utf-8 -*-

import random
from copter import *
import multiprocessing
from deap import creator, base, tools, algorithms


def generate_codons(aa_seq,
                    creator,
                    amino_to_codon_converter=amino_to_codon):
    codons = [amino_to_codon_converter(amino) for amino in aa_seq]
    return creator.Individual(codons)


def mutate_codon(individual,
                 codon_to_codon_converter=codon_to_codon,
                 indpb=0.05):
    for i in range(0, len(individual)):
        codon = individual[i]
        if random.random() < indpb:
            individual[i] = codon_to_codon_converter(codon)
    return individual, # mutation func should return tuple

def validate(individual,
             ng_sequences=[],
             validation_func=None):
    is_valid = True
    if ng_sequences is not None and len(ng_sequences) != 0:
        is_valid = not has_ng_sequences(individual, ng_sequences)
    if validation_func is not None:
        is_valid = validation_func(individual)
    return is_valid


def generate_population(toolbox,
                        population_size,
                        ng_sequences=[],
                        validation_func=None):
    # とりあえず100回くらいPopulationの生成を試み、駄目なら諦める
    for i in range(0, 100):
        population = toolbox.population(n=population_size)
        population = [ind for ind in population if validate(ind,
                                                            ng_sequences=ng_sequences,
                                                            validation_func=validation_func)]
        if len(population) > 0:
            return population
    return []

def optimize(aa_seq,
             eval_func,
             weights,
             validation_func=None,
             generation_size=100,
             population_size=100,
             indpb=0.05,
             surviver_amount=1,
             mutation_func=mutate_codon,
             amino_to_codon_converter=amino_to_codon,
             codon_to_codon_converter=codon_to_codon,
             ng_sequences=[]):
    toolbox = setup_toolbox(aa_seq,
                            weights,
                            surviver_amount=surviver_amount,
                            population_size=population_size,
                            indpb=indpb,
                            amino_to_codon_converter=amino_to_codon_converter,
                            codon_to_codon_converter=codon_to_codon_converter)
    population = generate_population(toolbox,
                                     population_size,
                                     ng_sequences=ng_sequences,
                                     validation_func=validation_func)
    if len(population) == 0:
        return []
    survivers = tools.selBest(population, k=surviver_amount)

    for gen in range(generation_size):
        new_population, survivers = evolve(population,
                                           survivers,
                                           eval_func,
                                           toolbox,
                                           population_size=population_size,
                                           surviver_amount=surviver_amount,
                                           ng_sequences=ng_sequences)
        if len(new_population) > 0:
            population = new_population
    surviver_genes = [''.join(codons) for codons in survivers]
    if validation_func is not None:
        surviver_genes = [gene for gene in surviver_genes if validation_func(gene)]
    return surviver_genes


def setup_toolbox(aa_seq,
                  weights,
                  surviver_amount=1,
                  population_size=100,
                  indpb=0.05,
                  amino_to_codon_converter=amino_to_codon,
                  codon_to_codon_converter=codon_to_codon):
    if surviver_amount > population_size:
        raise Exception('surviver_amount should be lower than population_size')

    creator.create("FitnessMax", base.Fitness, weights=weights)
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("individual", generate_codons, aa_seq, creator, amino_to_codon_converter=amino_to_codon)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mutate", mutate_codon, indpb=indpb, codon_to_codon_converter=codon_to_codon)
    return toolbox


def evolve(population,
           survivers,
           eval_func,
           toolbox,
           surviver_amount=1,
           population_size=1,
           ng_sequences=[]):
    dead_count = population_size - len(population)
    amplified_population = population + [creator.Individual(random.sample(population, 1)[0]) for i in range(0, dead_count)]

    # no cross over, 100% mutation(except for survivers)
    offspring = algorithms.varAnd(amplified_population, toolbox, cxpb=0, mutpb=1.0)
    offspring = offspring + survivers

    # remove genes that have ng_sequences
    if ng_sequences is not None and len(ng_sequences) != 0:
        offspring = [ind for ind in offspring if validate(ind, ng_sequences)]

    fits = toolbox.map(eval_func, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    survivers = tools.selBest(offspring, k=surviver_amount)
    new_population = tools.selBest(offspring, k=population_size)

    return new_population, survivers
