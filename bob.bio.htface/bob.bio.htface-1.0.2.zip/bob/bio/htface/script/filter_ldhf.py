#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
This click command take as input the scores from verify.py from LDHF database experiments and
filters them by distance (1m, 50m, 100m, 150m).
"""


import os
from bob.extension.scripts.click_helper import verbosity_option, ResourceOption
import click
from bob.extension import rc
import bob.io.base


@click.command(context_settings={'ignore_unknown_options': True,
                                 'allow_extra_args': True})
@click.argument('input_path', required=True)
def filter_ldhf(input_path, **kwargs):
    """
    This click command take as input the scores from verify.py from LDHF database experiments and
filters them by distance (1m, 50m, 100m, 150m).

    This code will go through all the available splits and generate
    subfolders for evert stand-off (1m, 50m, 100m, 150m)

    \b
    Example:
        $ bob bio htface filter_ldhf <PATH-TO-THE-EXPERIMENT>

    \b
    
    The above code will generate:
    <PATH-TO-THE-EXPERIMENT>_1m/split1/scores-dev
    <PATH-TO-THE-EXPERIMENT>_50m/split1/scores-dev
    <PATH-TO-THE-EXPERIMENT>_100m/split1/scores-dev
    ...
    <PATH-TO-THE-EXPERIMENT>_150m/splitn/scores-dev
 
    """

    #solving the / in the end
    if input_path[-1] == "/":
        input_path = input_path[0:-1]

    splits = os.listdir(input_path)
    experiment_dir_name = input_path.split("/")[-1]
    # for each split
    for split in splits:
    
        scores_filtered = dict()
        scores_filtered["1m"] = []
        scores_filtered["60m"] = []
        scores_filtered["100m"] = []
        scores_filtered["150m"] = []

        # getting the score file
        score_file = os.path.join(input_path, split, split, "nonorm", "scores-dev")
        scores = open(score_file)
            
        for s in scores:
           
            # searching the particular key
            for k in list(scores_filtered.keys()):
                
                if k in s:
                    scores_filtered[k].append(s)
                    break

        # Saving each score in its particular dir
        for k in list(scores_filtered.keys()):
            
            output_file_name = os.path.join(os.path.dirname(input_path), experiment_dir_name+"_"+k, split, "scores-dev")
            bob.io.base.create_directories_safe(os.path.dirname(output_file_name))
            f = open(output_file_name, "w")

            for l in scores_filtered[k]:
                f.write(l)


        pass  
           

