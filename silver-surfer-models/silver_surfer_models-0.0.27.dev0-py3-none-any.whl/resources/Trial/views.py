from sqlalchemy import and_

from src.silver_surfer_models.resources.Trial.models import TrialModel
from .schemas import TrialResourceSchema
from src.silver_surfer_models.database import db_session

schema = TrialResourceSchema()


def get_trial_ids_final_to_download():
    trial_query = db_session.query(TrialModel).filter(
        TrialModel.final_doc_id == None)  # noqa
    response = schema.dump(trial_query, many=True).data
    return response


def get_trial_ids_institution_to_download():
    trial_query = db_session.query(TrialModel).filter(
        TrialModel.institution_doc_id == None)  # noqa
    response = schema.dump(trial_query, many=True).data
    return response


def get_trials_w_null_final_file_ids_and_nn_final_doc_ids():
    trial_query = db_session.query(TrialModel).filter(
        and_(
            TrialModel.final_doc_id != None,  # noqa
            TrialModel.final_file_id == None,  # noqa
        ))
    response = schema.dump(trial_query, many=True).data
    return response


def get_trials_w_null_insti_file_ids_and_nn_insti_doc_ids():
    trial_query = db_session.query(TrialModel).filter(
        and_(
            TrialModel.institution_doc_id != None,  # noqa
            TrialModel.institution_file_id == None,  # noqa
        ))
    response = schema.dump(trial_query, many=True).data
    return response
