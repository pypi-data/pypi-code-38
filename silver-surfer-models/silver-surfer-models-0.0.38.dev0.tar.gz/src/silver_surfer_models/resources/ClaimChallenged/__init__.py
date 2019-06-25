from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from marshmallow import ValidationError
from collections import defaultdict

from ...database import db_session
from ...resources.ClaimChallenged.models import (
    ClaimChallengedModel,
)
from .schemas import (
    ClaimChallengedResourceSchema,
    ClaimChallengedQueryParamsSchema,
)


schema_resource = ClaimChallengedResourceSchema()
schema_params = ClaimChallengedQueryParamsSchema()


class ClaimChallengedNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class ClaimChallenged:
    @staticmethod
    def create(params):
        """
        :param
            ClaimChallengedResourceSchema
        :return:
            ClaimChallengedResourceSchema
        :exception:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_create(data)
        return response

    @staticmethod
    def read(params):
        """
        :param
            params: dict
                id
                claim_id
                prior_art_combination
                prior_art_id
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        claim_challenged_query = _build_query(params=data)
        response = schema_resource.dump(claim_challenged_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        :param
            params: dict
                id
                claim_id
                prior_art_combination
                prior_art_id
        :return:
            queried object
        :exception:
            ValidationError
        """

        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        claim_challenged_query = _build_query(params=data).one()
        response = schema_resource.dump(claim_challenged_query).data
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            ClaimChallengedNotFoundException
        """

        claim_challenged_query = db_session.query(
            ClaimChallengedModel).filter_by(
            id=id).first()
        if not claim_challenged_query:
            raise ClaimChallengedNotFoundException(
                'Claim challenged does not exist!')
        try:
            db_session.delete(claim_challenged_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise

    @staticmethod
    def bulk_delete(ptab2_proceeding_id):
        try:
            db_session.query(
                ClaimChallengedModel).filter(
                ClaimChallengedModel.ptab2_proceeding_id == ptab2_proceeding_id
            ).delete(synchronize_session=False)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise

    def view_combinations(self, claim_id, ptab2_proceeding_id):
        params = {
            'claim_id': claim_id,
            'ptab2_proceeding_id': ptab2_proceeding_id,
        }
        ccs = self.read(params)
        result = defaultdict(list)
        for cc in ccs:
            result[cc['prior_art_combination']].append({
                'prior_art_id': cc['prior_art_id'],
                'nature': cc['prior_art_nature'],
            })
        return result


def _helper_create(data):
    new_claim_challenged = ClaimChallengedModel(
        ptab2_proceeding_id=data['ptab2_proceeding_id'],
        claim_id=data['claim_id'],
        prior_art_combination=data['prior_art_combination'],
        prior_art_id=data['prior_art_id'],
        prior_art_nature=data['prior_art_nature'],
        updated_at=datetime.utcnow(),
    )
    try:
        db_session.add(new_claim_challenged)
        db_session.commit()
        claim_challenged_query = db_session.query(
            ClaimChallengedModel).get(
            new_claim_challenged.id)
        response = schema_resource.dump(claim_challenged_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(
        ClaimChallengedModel)
    if 'id' in params:
        q = q.filter_by(id=params['id'])
    if 'ptab2_proceeding_id' in params:
        q = q.filter_by(ptab2_proceeding_id=params['ptab2_proceeding_id'])
    if 'claim_id' in params:
        q = q.filter_by(claim_id=params['claim_id'])
    if 'prior_art_combination' in params:
        q = q.filter_by(
            prior_art_combination=params['prior_art_combination'])
    if 'prior_art_id' in params:
        q = q.filter_by(prior_art_id=params['prior_art_id'])
    if 'prior_art_nature' in params:
        q = q.filter_by(prior_art_nature=params['prior_art_nature'])
    return q
