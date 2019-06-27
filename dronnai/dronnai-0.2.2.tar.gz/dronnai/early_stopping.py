import time
import pdb
'''
TODO there should be developed class which can agreggate varius early stopping function in one instead of writing configurator per every stopping combination
'''


def conf_early_stopping_metric(patient,tolerance,max_patient):
    
    tolerance = 1-tolerance
    def early_stopping(obj):
        intervals_patient = int(obj.intervals_in_epoch * patient)
        max_intervals_patient = int(obj.intervals_in_epoch * max_patient)
        if intervals_patient >= len(obj.v_metrics[obj.names[0]]):
            return False, None

        best_metric = obj.metric[0].get_best(obj.v_metrics[obj.names[0]])
        best_pos = obj.v_metrics[obj.names[0]].index(best_metric)
        if len(obj.v_metrics[obj.names[0]]) - best_pos > intervals_patient:
            tolerant_best = best_metric * tolerance
            actual_metric = obj.v_metrics[obj.names[0]][-1]
            if obj.metric[0].get_best([tolerant_best,actual_metric]) == tolerant_best:
                return True, 'Lack of metric improvement.'
            if obj.metric[0].get_best([best_metric,actual_metric]) == best_metric and max_intervals_patient <= len(obj.v_metrics[obj.names[0]]):
                return True, 'Lack of metric improvement.'
        return False, None
    return early_stopping


def conf_early_stopping_loss(patient,tolerance,max_patient):
    tolerance = 1-tolerance
    def early_stopping(obj):
        # intervals_patient could be pre-computed in conf or somewhere else
        intervals_patient = int(obj.intervals_in_epoch * patient)
        max_intervals_patient = int(obj.intervals_in_epoch * max_patient)
        if intervals_patient >= len(obj.v_losses[obj.names[0]]):
            return False, None
        best_loss = min(obj.v_losses[obj.names[0]])
        best_pos = obj.v_losses[obj.names[0]].index(best_loss)
        if len(obj.v_losses[obj.names[0]]) - best_pos > intervals_patient:
            tolerant_best = best_loss * tolerance
            actual_loss = obj.v_losses[obj.names[0]][-1]
            if min([tolerant_best,actual_loss]) == tolerant_best:
                return True, 'Lack of loss decrease.'
            if min([best_loss,actual_loss]) == best_loss and max_intervals_patient <= len(obj.v_losses[obj.names[0]]):
                return True, 'Lack of loss decrease.'
        return False, None
    return early_stopping


def conf_early_stopping_all(patient,tolerance,max_patient):
    es_loss = conf_early_stopping_loss(patient,tolerance,max_patient)
    es_metric = conf_early_stopping_metric(patient,tolerance,max_patient)
    def early_stopping(obj):
        stop1, reason1 = es_loss(obj)
        stop2, reason2 = es_metric(obj)
        if stop1 and stop2:
            print('Stopping - lack of improvement.')
            return True, '{} {}'.format(reason1,reason2)
        else:
            return False
    return early_stopping

def conf_early_stopping_all_time(patient,tolerance,max_patient,time_stop):
    es_loss = conf_early_stopping_loss(patient,tolerance,max_patient)
    es_metric = conf_early_stopping_metric(patient,tolerance,max_patient)
    def early_stopping(obj):
        stop1, reason1 = es_loss(obj)
        stop2, reason2 = es_metric(obj)
        if stop1 and stop2:
            print('Stopping - lack of improvement.')
            return True, '{} {}'.format(reason1,reason2)
        elif time.time() - obj.time_start > time_stop:
            print('Stopping - too time consuming.')
            return True, 'Too time consuming.'
        else:
            return False, None
    return early_stopping