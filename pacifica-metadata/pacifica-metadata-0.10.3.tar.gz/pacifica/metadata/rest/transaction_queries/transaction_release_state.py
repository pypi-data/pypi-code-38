#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Transaction Metadata object class."""
from cherrypy import tools, request
from pacifica.metadata.rest.transaction_queries.query_base import QueryBase
from pacifica.metadata.orm import TransactionUser, DOITransaction, CitationTransaction, Relationships
from pacifica.metadata.rest.user_queries.user_lookup import UserLookup
from pacifica.metadata.orm.base import db_connection_decorator


class TransactionReleaseState(QueryBase):
    """Retrieves release state for an individual transaction (GET) or set of transactions (POST)."""

    exposed = True

    @staticmethod
    def _get_release_state(transaction_list):
        releases = TransactionReleaseState._get_release_info(transaction_list)

        output_results = {}
        user_lookup_cache = {}
        found_transactions = []

        transactions = QueryBase._get_transaction_sizes(transaction_list)

        for release in releases:
            found_transactions.append(release['transaction'])
            # NOTE: we should change this back to authorized_user with relationship link
            if release['user'] not in user_lookup_cache:
                user_lookup_cache[release['user']] = UserLookup.get_user_info_block(
                    release['user'], 'simple')
            release.update({
                'user': user_lookup_cache[release['user']],
                'release_state': 'released', 'display_state': 'Released',
                'release_date': release['release_date'].isoformat(),
                'total_size_bytes': transactions[release['transaction']]['total_file_size_bytes'],
                'total_file_count': transactions[release['transaction']]['total_file_count'],
                'release_doi_entries': TransactionReleaseState._get_doi_release(release['transaction']),
                'release_citations': TransactionReleaseState._get_citation_release(release['transaction'])
            })
            output_results[release['transaction']] = release

        missing_transactions = TransactionReleaseState._generate_missing_transactions(
            transaction_list, found_transactions
        )
        output_results.update(missing_transactions)

        return output_results

    @staticmethod
    def _generate_missing_transactions(transaction_list, found_transactions):
        output_results = {}
        missing_transactions = list(
            set(transaction_list) - set(found_transactions))
        for txn in missing_transactions:
            output_results[txn] = {
                'user': None, 'release_state': 'not_released',
                'display_state': 'Not Released', 'transaction': txn
            }
        return output_results

    @staticmethod
    def _get_release_info(transaction_list):
        # pylint: disable=no-member
        releases = (TransactionUser
                    .select(TransactionUser.transaction,
                            TransactionUser.user,
                            TransactionUser.updated.alias('release_date'))
                    .join(Relationships)
                    .where(
                        (TransactionUser.transaction << transaction_list)
                    ).dicts())
        # pylint: enable=no-member
        return releases

    @staticmethod
    def _get_doi_release(transaction_id):
        output_results = None
        rel_obj = Relationships.get(Relationships.name == 'authorized_releaser')
        # pylint: disable=no-member
        doi_releases = (DOITransaction
                        .select()
                        .join(TransactionUser)
                        .where(
                            (TransactionUser.relationship == str(rel_obj.uuid)) &
                            (DOITransaction.transaction == TransactionUser.uuid) &
                            (TransactionUser.transaction == transaction_id)
                        ))
        # pylint: enable=no-member
        if doi_releases.exists():
            output_results = []
            for release in doi_releases:
                # mint_api = release.doi.metadata.where(release.doi.metadata.key == 'minting_api_id')
                # print(mint_api)
                metadata = {info_bit.__data__['key']: info_bit.__data__[
                    'value'] for info_bit in release.doi.metadata}
                output_results.append({
                    'doi_status': release.doi.status,
                    'is_released': release.doi.released,
                    'doi_reference': release.doi.doi,
                    'site_url': release.doi.site_url,
                    'submission_date': release.created.isoformat(),
                    'metadata': metadata
                })
        return output_results

    @staticmethod
    def _get_citation_release(transaction_id):
        output_results = None
        rel_obj = Relationships.get(Relationships.name == 'authorized_releaser')
        # pylint: disable=no-member
        citation_releases = (CitationTransaction
                             .select()
                             .join(TransactionUser)
                             .where(
                                 (TransactionUser.relationship == str(rel_obj.uuid)) &
                                 (CitationTransaction.transaction == TransactionUser.uuid) &
                                 (TransactionUser.transaction == transaction_id)
                             ))
        # pylint: enable=no-member
        if citation_releases.exists():
            output_results = []
            for citation_entry in citation_releases:
                output_results.append(
                    {
                        'citation_id': citation_entry.citation.id,
                        'title': citation_entry.citation.article_title,
                        'doi_reference': citation_entry.citation.doi_reference
                    }
                )
        return output_results

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(trans_id=None):
        """Return release details about the specified transaction entity."""
        return TransactionReleaseState._get_release_state((int(trans_id),))

    # pylint: disable=duplicate-code
    @staticmethod
    @tools.json_out()
    @tools.json_in()
    @db_connection_decorator
    # pylint: enable=duplicate-code
    def POST():
        """Return transaction release state details for the list of transaction_id's."""
        transaction_list = [int(trans_id) for trans_id in request.json]
        return TransactionReleaseState._get_release_state(transaction_list)
