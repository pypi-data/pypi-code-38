#!/usr/bin/python3

"""
The moiety_modeling command-line interface option
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
    moiety_modeling -h | --help
    moiety_modeling --version
    moiety_modeling modeling [--combinedData=<combined_jsonfile>] [--models=<models_jsonfile] [--datasets=<datasets_jsonfile>] [--optimizations=<optimizations_jsonfile>] [--working=<working_dir>] [--repetition=<optim_count>] [--split] [--force] [--multiprocess] [--energyFunction=<function>] [--printOptimizationScripts]
    moiety_modeling analyze optimizations --a <optimizationPaths_txtfile>  [--working=<working_dir>]
    moiety_modeling analyze optimizations --s <optimizationResults_jsonfile> [--working=<working_dir>]
    moiety_modeling analyze rank <analysisPaths_txtfile> [--working=<working_dir>] [--rankCriteria=<rankCriteria>]
    moiety_modeling analyze table <rankPaths_txtfile> [--working=<working_dir>]
    moiety_modeling plot moiety <analysisResults_jsonfile> [--working=<working_dir>]
    moiety_modeling plot isotopologue <analysisResults_jsonfile> [--working=<working_dir>]

Options:
    -h, --help                                       Show this screen.
    --version                                        Show version.
    --combinedData=<combined_jsonfile>               JSON description file of the combined data (eg: models, datasets, optimization settings)
    --models=<models_jsonfile>                       JSON description file of the moiety models.
    --datasets=<datasets_jsonfile>                   JSON description file of the datasets.
    --optimizations=<optimizations_jsonfile>         JSON description file of the optimization setting.
    --working=<working_dir>                          Alternative path to save the results.
    --repetition=<optim_count>                       The number of optimization repetitions to perform [default: 100].
    --split                                          To split the datasets or not.
    --force                                          To force optimization process if error occurs.
    --multiprocess                                   To perform with multiprocessing or not.
    --printOptimizationScripts                       To print the optimization script or not.
    --a                                              To analyze a bunch of optimization results together with the path file.
    --s                                              To analyze a single moiety model optimization results.
    --energyFunction=<enegyFunction>                 The energyFunction of the moiety modeling optimization.
    --optimizationSetting=<optimizationSetting>      The optimization setting of the moiety modeling optimization.
    --rankCriteria=<rankCriteria>                    The criteria for model ranking [default: AICc].
"""

import jsonpickle
import os
from . import modeling
from . import analysis


def cli(args):

    if args['modeling']:

        dirName = ''

        combinedData = {}
        if args['--combinedData']:
            dirName += os.path.splitext(os.path.basename(args['--combinedData']))[0] + '_'
            with open(args['--combinedData']) as combinedFile:
                combinedData = jsonpickle.decode(combinedFile.read())

        if args['--models']:
            dirName += os.path.splitext(os.path.basename(args['--models']))[0] + '_'
            with open(args['--models']) as modelFile:
                models = jsonpickle.decode(modelFile.read())['models']
        elif 'models' in combinedData:
            models = combinedData['models']
        else:
            raise ImportError("Model is missing!")

        if args['--datasets']:
            dirName += os.path.splitext(os.path.basename(args['--datasets']))[0] + '_'
            with open(args['--datasets']) as datasetFile:
                datasets = jsonpickle.decode(datasetFile.read())['datasets']
        elif 'datasets' in combinedData:
            datasets = combinedData['datasets']
        else:
            raise ImportError("Dataset is missing!")

        if args['--optimizations']:
            dirName += os.path.splitext(os.path.basename(args['--optimizations']))[0] + '_'
            with open(args['--optimizations']) as settingFile:
                optimizations = jsonpickle.decode(settingFile.read())['optimizations']
        elif 'optimizations' in combinedData:
            optimizations = combinedData['optimizations']
        else:
            raise ImportError("Optimization setting is missing!")

        times = int(args['--repetition']) if args['--repetition'] else 100
        dirName += 'T_{0}_'.format(times)

        dirName += 'S_' if args['--split'] else 'noS_'

        dirName += 'M_' if args['--multiprocess'] else 'noM_'

        energyFunction = args['--energyFunction'] if args['--energyFunction'] else 'logDifference'
        dirName += energyFunction

        if args['--working']:
            os.mkdir(args['--working'] + '/' + dirName)
            path = args['--working'] + '/' + dirName

        else:
            if args['--datasets']:
                datasetPath = os.path.dirname(args['--datasets'])
                os.mkdir(datasetPath + '/' + dirName)
                path = datasetPath + '/' + dirName

            else:
                combinedPath = os.path.dirname(args['--combinedData'])
                os.mkdir(combinedPath + '/' + dirName)
                path = combinedData + '/' + dirName

        manager = modeling.OptimizationManager(models, datasets, optimizations, path, args['--split'], args['--multiprocess'], args['--force'], times, energyFunction, args['--printOptimizationScripts'])
        manager.optimizeModels()

    elif args['analyze'] or args['plot']:

        if args['optimizations']:
            if args['--a']:
                base = os.path.basename(args['<optimizationPaths_txtfile>'])
                baseName = os.path.splitext(base)[0]
                path = args['--working'] if args['--working'] else '{0}/{1}_analysis/'.format(os.path.dirname(args['<optimizationPaths_txtfile>']), baseName)
                os.mkdir(path)
                analysisPathFile = open('{0}{1}_analysis.txt'.format(path, baseName), 'w')
                with open(args['<optimizationPaths_txtfile>']) as pathFile:
                    for fileName in pathFile:
                        resAnalysis = analysis.ResultsAnalysis(fileName.replace("\n", ""), path)
                        resAnalysis.analyze()
                        analysisPathFile.write(resAnalysis.jsonfilePath + '\n')
                analysisPathFile.close()
            elif args['--s']:
                path = args['--working'] if args['--working'] else None
                resAnalysis = analysis.ResultsAnalysis(args['<optimizationResults_jsonfile>'], path)
                resAnalysis.analyze()
            else:
                raise ImportError("Something is missing for optimization analysis!")

        elif args['rank']:
            if args['<analysisPaths_txtfile>']:
                path = args['--working'] if args['--working'] else None
                selectionCriteria = args['--rankCriteria'] if args['--rankCriteria'] else 'AICc'
                modelRank = analysis.ModelRank(args['<analysisPaths_txtfile>'], path, selectionCriteria)
                modelRank.rank()
            else:
                raise ImportError("Result path file is missing for model rank!")

        elif args['table']:
            if args['<rankPaths_txtfile>']:
                path = args['--working'] if args['--working'] else None
                comparisonTable = analysis.ComparisonTable(args['<rankPaths_txtfile>'], path)
                comparisonTable.makeTable()
            else:
                raise ImportError("Rank path file is missing for comparison table!")

        elif args['moiety']:
            if args['<analysisResults_jsonfile>']:
                path = args['--working'] if args['--working'] else None
                moietyPlot = analysis.PlotMoietyDistribution(args['<analysisResults_jsonfile>'], path)
                moietyPlot.plotMoiety()
            else:
                ImportError("Analysis results jsonfile is missing for moiety distribution plot!")

        elif args['isotopologue']:
            if args['<analysisResults_jsonfile>']:
                path = args['--working'] if args['--working'] else None
                isotopologuePlot = analysis.PlotIsotopologueIntensity(args['<analysisResults_jsonfile>'], path)
                isotopologuePlot.plotIsotopologue()
            else:
                ImportError("Analysis results jsonfile is missing for observed and calculated isotoplogue comparison!")








