import pandas as pd
from flatten_dict import flatten
from sacred import Experiment

def exp_recorder(exp_name,args,metrics,mongo_connector):
    """
    Function which will store output of your exp
    exp_name: name of your experiment
    args: dict with args used in exp
    metrics: output of gym.workout
    mongo_connector: sacred.observers.MongoObserver object which handle connection with database
    """
    ex = Experiment(exp_name)
    ex.observers.append(mongo_connector)
    flatten_args = flatten(args,reducer=lambda a,b: '{}_{}'.format(a,b) if a else b)
    flatten_args['true_args'] = args
    ex.add_config(flatten_args)
    result = metrics[list(metrics)[0]]['best_valid_metric']

    @ex.main
    def store():
        metric_store(metrics,ex)
        return result
    ex.run()

def metric_store(results,ex,prefix=''):
    """
    helper function to iterate over nasted dict created to handle and store gym metrics and losses
    """
    print(results)
    for result in results:
        if isinstance(results[result],dict):
            metric_store(results[result],ex,'{}.{}'.format(prefix,result))
        else:
            for scalar in results[result]:
                ex.log_scalar('{}.{}'.format(prefix,result)[1:-1],scalar)
                
def exp_downloader(exp_name,mongo_connector):
    """
    exp_name: name of expermient used to store outcome in MongoDB
    mongo_connector: pymnogo.MongoClient object connected to database
    """
    db = mongo_connector.ai
    cursor = db.runs.find({'experiment.name':exp_name})
    exp_list = []
    true_list = []
    for exp in cursor:
        new_exp = exp['config']
        true_args = new_exp.pop('true_args')
        exp_list.append(new_exp)
        true_list.append(true_args)
    
    return pd.concat([pd.DataFrame(exp) for exp in exp_list]), true_list
    