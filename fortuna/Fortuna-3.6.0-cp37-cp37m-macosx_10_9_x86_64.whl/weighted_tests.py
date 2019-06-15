from Fortuna import *


print("\nWeighted Tables:\n")
population = ("A", "B", "C", "D")

cum_weights = (1, 3, 6, 10)
rel_weights = (1, 2, 3, 4)

cum_weighted_table = zip(cum_weights, population)
rel_weighted_table = zip(rel_weights, population)


cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
distribution_timer(cum_weighted_choice)

rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
distribution_timer(rel_weighted_choice)
