
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import logging

from squid_py.data_store.storage_base import StorageBase

logger = logging.getLogger(__name__)


class AgreementsStorage(StorageBase):
    """
    Provide storage for SEA service agreements in an sqlite3 database.
    """
    def record_service_agreement(self, service_agreement_id, did, service_definition_id, price,
                                 files, start_time, status='pending'):
        """
        Records the given pending service agreement.

        :param service_agreement_id: hex str the id of the service agreement used as primary key
        :param did: DID, str in the format `did:op:0xXXX`
        :param service_definition_id: identifier of the service inside the asset DDO, str
        :param price: Asset price, int
        :param files: hex str encrypted files list
        :param start_time: str timestamp capturing the time this agreement was initiated
        :param status: str indicates the current status (pending, completed, aborted)
        :return:
        """
        logger.debug(f'Recording agreement info to `service_agreements` storage: '
                     f'agreementId={service_agreement_id}, did={did},'
                     f'service_definition_id={service_definition_id}, price={price}')
        self._run_query(
            '''CREATE TABLE IF NOT EXISTS service_agreements
               (id VARCHAR PRIMARY KEY, did VARCHAR, service_definition_id INTEGER,
                price VARCHAR, files VARCHAR, start_time INTEGER, status VARCHAR(10));'''
        )
        self._run_query(
            'INSERT OR REPLACE INTO service_agreements VALUES (?,?,?,?,?,?,?)',
            (service_agreement_id, did, service_definition_id,
             str(price), files, start_time, status),
        )

    def update_status(self, service_agreement_id, status):
        """
        Update the service agreement status.

        :param service_agreement_id: hex str the id of the service agreement used as primary key
        :param status: str indicates the current status (pending, completed, aborted)
        :return:
        """
        logger.debug(f'Updating agreement {service_agreement_id} status to {status}')
        self._run_query(
            'UPDATE service_agreements SET status=? WHERE id=?',
            (status, service_agreement_id),
        )

    def get_service_agreements(self, status='pending'):
        """
        Get service agreements matching the given status.

        :param status: str indicates the current status (pending, completed, aborted)
        :return:
        """
        return [
            row for row in
            self._run_query(
                '''
                    SELECT id, did, service_definition_id, price, files, start_time, status
                    FROM service_agreements
                    WHERE status=?;
                ''',
                (status,))
        ]

    def get_agreement_ids(self, status=None):
        """Return all known agreement ids.
        If status is set, only agreements matching this status will be returned.

        :param status: str indicates the current status (pending, completed, aborted)
        """
        try:
            query, args = "SELECT id FROM service_agreements", ()
            if status is not None:
                args = (status,)
                query += " WHERE status=?"

            agreement_ids = {row[0] for row in self._run_query(query, args)}
            logger.debug(f'Read agreement ids from `service_agreements` storage: '
                         f'agreementIds={agreement_ids}')
            return agreement_ids
        except Exception as e:
            logger.error(f'db error getting agreement ids: {e}')
            return []
