"""
Provides a function for the ehub_model using an epsilon constraint method

for input and output files - use config.yaml

To run: specify the number of intervals wanted for epsilon constraint method in the arguments

            $ python epsilon_constraint.py --epsilon_n N
"""
from energy_hub import EHubModel
from run import CarbonEHubModel
import yaml
from outputter import pretty_print, output_excel
import argparse

""" Loads a yaml file """
#TODO: yaml loader & check if file exists
with open("config.yaml", "r") as file_descriptor:
    data = yaml.safe_load(file_descriptor)


def main(epsilon_n):
    """
    Main function for running the EHub_Model using the epsilon constraint method

    :param epsilon_n: number of divisions wanted for the epsilon constraint method

    :outputs excel files with all the data (including the points in between)
    """

    outputFile = data['output_file']

    if epsilon_n is None:
        epsilon_n = 0

    # calculating the minimum cost using the EHubModel(with the maximum carbon)
    cost_min_model = EHubModel(excel=data['input_file'])
    cost_min = cost_min_model.solve(data['solver'])

    # calculating the carbon per each step of the division from the maximum carbon for epsilon_n != 0.
    carbon_per_step = 0 if epsilon_n == 0 else (cost_min['solution']['total_carbon']) / epsilon_n

    # loop that goes through all the point between the min carbon (max cost) and min cost(max carbon )
    # if epsilon_n = 0, outputs only the min carbon to the excel file
    for n in range(epsilon_n+1):

        # calculating the the points in between the two minimums, while changing the carbon constraint with
        # each iteration in the CarbonEHubModel
        carbon_min_model = CarbonEHubModel(excel=data['input_file'], max_carbon=carbon_per_step * n)
        carbon_min = carbon_min_model.solve(data['solver'])
        pretty_print(carbon_min)

        # outputs the results to separate excel files with the numbers at the end of the name from 0 - n
        # file with number 0 - displays minimizing carbon
        # file with number n - displays minimizing cost
        output_excel(carbon_min['solution'], outputFile[:-5] + "_" + str(n) + '.xlsx',
                     time_steps=len(carbon_min_model.time))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--epsilon_n', type=int,
                        help='The number of steps to break into for the epsilon constraint.')

    arg = parser.parse_args()

    main(arg.epsilon_n)
