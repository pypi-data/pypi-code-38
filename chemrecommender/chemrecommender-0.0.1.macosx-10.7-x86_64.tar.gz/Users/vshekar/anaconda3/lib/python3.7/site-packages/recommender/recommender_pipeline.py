import json
import os
import numpy as np
import pandas as pd
from recommender.generator import Generator, MLmodel
from recommender.mutual_information import MutualInformation, DESCRIPTORS_TO_REMOVE

# This file shows an application of the recommender pipeline with the help
# of an example

"""
Steps to implement a recommender pipeline

1) Generate reaction features
    - Get the chemicals in a reaction. For DRP these are referred to as triples
    - Generate descriptors for each of the chemicals in the reaction
    - Generate a sampling grid of reaction parameters
    - Expand grid by associating descriptors with each point on the grid

2) Run trained models with the reaction Sieve
    - Get a trained machine learning model
    - Filter sampling grid by running it through the ML model
    - Make a list of all the potentially successful reactions
      as predicted by the ML model

3) Recommend reactions
    - Calculate the mutual information of the potential reactions
      as compared to the already completed reactions
    - Select the top 'k' reactions with the highest MI


"""


def generate_reaction_grid():
    # Setting up reaction parameters
    grid_params_filename = '../sample_data/grid_params.json'
    compounds_filename = '../sample_data/triples_and_amounts.json'
    reaction_generator = Generator(compounds_filename, grid_params_filename)

    # Generate a reaction grid with only the compounds and their parameters
    reaction_generator.generate_grid()

    # Generate descriptors of all the compounds in the data given
    descriptor_list_file = '../sample_data/descriptors_list.json'
    reaction_generator.generate_descriptors(descriptor_list_file)

    # Combine the grid with the generated descriptors
    reaction_generator.generate_expanded_grid()

    return reaction_generator


def reaction_sieve(reaction_generator):
    # Setup machine learning model
    model = MLmodel()
    potential_reactions = model.sieve(reaction_generator.all_combos_expanded)
    return potential_reactions


def recommend(potential_reactions, top_k):

    dataset = pd.read_csv(
        '../sample_data/test_data_full.csv', low_memory=False)
    dataset_org = dataset.iloc[:6000]
    dataset_new = dataset.iloc[-100:]
    descriptors_to_keep = [
        col for col in dataset.columns if col not in DESCRIPTORS_TO_REMOVE]
    desc_to_keep_testing = [col for col in dataset.columns if col not in DESCRIPTORS_TO_REMOVE] + [
        'boolean_crystallisation_outcome_manual_0']
    dataset_new = dataset_new[desc_to_keep_testing].values
    compound_column_labels = ['compound_0', 'compound_1', 'compound_2']
    mi = MutualInformation(
        dataset_org, 'boolean_crystallisation_outcome_manual_0', compound_column_labels, descriptors_to_keep)
    recommended_reactions = mi.get_recommended_reactions(
        top_k, potential_reactions[[col for col in potential_reactions.columns if col not in DESCRIPTORS_TO_REMOVE]])
    return recommended_reactions


if __name__ == "__main__":
    os.environ['CXCALC_PATH'] = '/Applications/MarvinSuite/bin'
    reaction_generator = generate_reaction_grid()
    pred_sucessful_reaction = reaction_sieve(reaction_generator)
    recommended_reactions = recommend(pred_sucessful_reaction, 10)
    print(recommended_reactions)
