import logging
from enum import Enum

from polyswarmartifact import ArtifactType

from polyswarmclient import bloom
from polyswarmclient.verifiers import NctApproveVerifier, \
    PostBountyVerifier, PostAssertionVerifier, RevealAssertionVerifier, \
    PostVoteVerifier, SettleBountyVerifier
from polyswarmclient.transaction import AbstractTransaction
from polyswarmclient.parameters import Parameters
from polyswarmclient.utils import bool_list_to_int, calculate_commitment

logger = logging.getLogger(__name__)


class PostBountyTransaction(AbstractTransaction):
    def __init__(self, client, artifact_type, amount, bounty_fee, artifact_uri, num_artifacts, duration, bloom):
        self.amount = amount
        self.artifact_type = artifact_type
        self.artifact_uri = artifact_uri
        self.duration = duration

        approve = NctApproveVerifier(amount + bounty_fee)
        bounty = PostBountyVerifier(artifact_type, amount, artifact_uri, num_artifacts, duration, bloom)

        super().__init__(client, [approve, bounty])

    def get_path(self):
        return "/bounties"

    def get_body(self):
        return {
            "amount": str(self.amount),
            "artifact_type": self. artifact_type,
            "uri": self.artifact_uri,
            "duration": self.duration
        }

    def has_required_event(self, transaction_events):
        bounties = transaction_events.get('bounties', [])
        for bounty in bounties:
            if (bounty.get('amount', '') == str(self.amount) and
                    bounty.get('uri', '') == self.artifact_uri):
                return True

        return False


class PostAssertionTransaction(AbstractTransaction):
    def __init__(self, client, bounty_guid, bid, assertion_fee, mask, commitment):
        self.bounty_guid = bounty_guid
        self.bid = bid
        self.assertion_fee = assertion_fee
        self.mask = mask
        self.commitment = commitment

        approve = NctApproveVerifier(bid + assertion_fee)
        assertion = PostAssertionVerifier(bounty_guid, bid, mask, commitment)

        super().__init__(client, [approve, assertion])

    def get_body(self):
        return {
            'bid': str(self.bid),
            'mask': self.mask,
            'commitment': str(self.commitment),
        }

    def get_path(self):
        return '/bounties/{0}/assertions'.format(self.bounty_guid)

    def has_required_event(self, transaction_events):
        assertions = transaction_events.get('assertions', [])
        for assertion in assertions:
            if (assertion.get('bid', '') == str(self.bid) and
                    assertion.get('mask', []) == self.mask and
                    assertion.get('commitment', '') == str(self.commitment) and
                    assertion.get('bounty_guid', '') == self.bounty_guid):
                return True

        return False


class RevealAssertionTransaction(AbstractTransaction):
    def __init__(self, client, bounty_guid, index, nonce, verdicts, metadata):
        self.verdicts = verdicts
        self.metadata = metadata
        self.nonce = nonce
        self.guid = bounty_guid
        self.index = index
        reveal = RevealAssertionVerifier(bounty_guid, index, nonce, verdicts, metadata)
        super().__init__(client, [reveal])

    def get_path(self):
        return '/bounties/{0}/assertions/{1}/reveal'.format(self.guid, self.index)

    def get_body(self):
        return {
            'nonce': str(self.nonce),
            'verdicts': self.verdicts,
            'metadata': self.metadata,
        }

    def has_required_event(self, transaction_events):
        reveals = transaction_events.get('reveals', [])
        for reveal in reveals:
            if (reveal.get('verdicts', []) == self.verdicts and
                    reveal.get('metadata', '') == self.metadata and
                    reveal.get('bounty_guid', '') == self.guid):
                return True

        return False


class PostVoteTransaction(AbstractTransaction):
    def __init__(self, client, bounty_guid, votes, valid_bloom):
        self.votes = votes
        self.valid_bloom = valid_bloom
        self.guid = bounty_guid
        vote = PostVoteVerifier(bounty_guid, votes, valid_bloom)
        super().__init__(client, [vote])

    def get_path(self):
        return '/bounties/{0}/vote'.format(self.guid)

    def get_body(self):
        return {
            'votes': self.votes,
            'valid_bloom': self.valid_bloom,
        }

    def has_required_event(self, transaction_events):
        votes = transaction_events.get('votes', [])
        for vote in votes:
            if (vote.get('votes', []) == self.votes and
                    vote.get('bounty_guid', '') == self.guid):
                return True

        return False


class SettleBountyTransaction(AbstractTransaction):
    def __init__(self, client, bounty_guid):
        self.guid = bounty_guid
        settle = SettleBountyVerifier(bounty_guid)
        super().__init__(client, [settle])

    def get_path(self):
        return '/bounties/{0}/settle'.format(self.guid)

    def get_body(self):
        return None

    def has_required_event(self, transaction_events):
        # Settle events are not reported by polyswarmd, transfers are but are not guaranteed
        return True


class BountiesClient(object):
    def __init__(self, client):
        self.__client = client
        self.parameters = {}

    async def fetch_parameters(self, chain, api_key=None):
        """Get bounty parameters from polyswarmd.

        Args:
            chain (str): Which chain to operate on.
            api_key (str): Override default API key
        Note:
            This function doesn't return anything. It instead stores the bounty parameters
            as parsed JSON in self.parameters[chain].
        """
        success, result = await self.__client.make_request('GET', '/bounties/parameters', chain, api_key=api_key)
        if not success:
            raise Exception('Error retrieving bounty parameters')

        self.parameters[chain] = Parameters(result)

    async def calculate_bloom(self, ipfs_uri, api_key=None):
        """Calculate bloom filter for a set of artifacts.

        Args:
            ipfs_uri (str): IPFS URI for the artifact set
            api_key (str): Override default API key
        Returns:
            Bloom filter value for the artifact set
        """
        artifacts = await self.__client.list_artifacts(ipfs_uri, api_key=api_key)
        bf = bloom.BloomFilter()
        for _, h in artifacts:
            bf.add(h.encode('utf-8'))

        return int(bf)

    async def get_bloom(self, bounty_guid, chain, api_key=None):
        """
        Get bloom from polyswamrd

        Args:
            bounty_guid (str): GUID of the bounty to retrieve the vote from
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        """
        path = '/bounties/{0}/bloom'.format(bounty_guid)
        success, result = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.error('Expected bloom, received', extra={'extra': result})
            return None
        return result.get('bloom')

    async def get_bounty(self, guid, chain, api_key=None):
        """Get a bounty from polyswarmd.

        Args:
            guid (str): GUID of the bounty to retrieve
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing bounty details
        """
        path = '/bounties/{0}'.format(guid)
        success, result = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.error('Expected bounty, received', extra={'extra': result})
            return None

        return result

    async def post_bounty(self, artifact_type, amount, artifact_uri, duration, chain, api_key=None):
        """Post a bounty to polyswarmd.

        Args:
            artifact_type (ArtifactType): The artifact type in this bounty
            amount (int): The amount to put up as a bounty
            artifact_uri (str): URI of artifacts
            duration (int): Number of blocks to accept new assertions
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing emitted events
        """
        bounty_fee = await self.parameters[chain].get('bounty_fee')
        bloom = await self.calculate_bloom(artifact_uri)
        num_artifacts = await self.__client.get_artifact_count(artifact_uri)
        transaction = PostBountyTransaction(self.__client, ArtifactType.to_string(artifact_type), amount, bounty_fee,
                                            artifact_uri, num_artifacts, duration, bloom)
        success, result = await transaction.send(chain, api_key=api_key)

        if not success or 'bounties' not in result:
            logger.error('Expected bounty, received', extra={'extra': result})

        return result.get('bounties', [])

    async def get_assertion(self, bounty_guid, index, chain, api_key=None):
        """Get an assertion from polyswarmd.

        Args:
            bounty_guid (str): GUID of the bounty to retrieve the assertion from
            index (int): Index of the assertion
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing assertion details
        """
        path = '/bounties/{0}/assertions/{1}'.format(bounty_guid, index)
        success, result = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.error('Expected assertion, received', extra={'extra': result})
            return None

        return result

    async def get_all_assertions(self, bounty_guid, chain, api_key=None):
        """Get an assertion from polyswarmd.

        Args:
            bounty_guid (str): GUID of the bounty to retrieve the assertion from
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing assertion details
        """
        path = '/bounties/{0}/assertions'.format(bounty_guid)
        success, result = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.error('Expected assertion, received', extra={'extra': result})
            return None

        return result

    async def post_assertion(self, bounty_guid, bid, mask, verdicts, chain, api_key=None):
        """Post an assertion to polyswarmd.

        Args:
            bounty_guid (str): The bounty to assert on
            bid (int): The amount to bid
            mask (List[bool]): Which artifacts in the bounty to assert on
            verdicts (List[bool]): Verdict (malicious/benign) for each of the artifacts in the bounty
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing emitted events
        """
        fee = await self.parameters[chain].get('assertion_fee')
        nonce, commitment = calculate_commitment(self.__client.account, bool_list_to_int(verdicts))

        transaction = PostAssertionTransaction(self.__client, bounty_guid, bid, fee, mask, commitment)
        success, result = await transaction.send(chain, api_key=api_key)
        if not success or 'assertions' not in result:
            logger.error('Expected assertions, received', extra={'extra': result})

        return nonce, result.get('assertions', [])

    async def post_reveal(self, bounty_guid, index, nonce, verdicts, metadata, chain, api_key=None):
        """Post an assertion reveal to polyswarmd.

        Args:
            bounty_guid (str): The bounty which we have asserted on
            index (int): The index of the assertion to reveal
            nonce (str): Secret nonce used to reveal assertion
            verdicts (List[bool]): Verdict (malicious/benign) for each of the artifacts in the bounty
            metadata (str): Optional metadata
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing emitted events
        """

        transaction = RevealAssertionTransaction(self.__client, bounty_guid, index, nonce, verdicts, metadata)

        success, result = await transaction.send(chain, api_key=api_key)
        if not success or 'reveals' not in result:
            logger.error('Expected reveal, received', extra={'extra': result})

        return result.get('reveals', [])

    async def post_metadata(self, metadata, chain, api_key=None):
        """Posts metadata to IPFS

        Args:
            metadata (str): metadata json that conforms to Assertion Schema in polyswarm-artifact
            chain (str): Which chain to operate on
            api_key (str): Override default API key

        Returns: ipfs_hash or None

        """
        success, ipfs_hash = await self.__client.make_request('POST', '/bounties/metadata', chain,
                                                              json=metadata,
                                                              api_key=api_key)
        return ipfs_hash if success else None

    async def get_vote(self, bounty_guid, index, chain, api_key=None):
        """
        Get a vote from polyswamrd

        Args:
            bounty_guid (str): GUID of the bounty to retrieve the vote from
            index (int): Index of the vote
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        """
        path = '/bounties/{0}/votes/{1}'.format(bounty_guid, index)
        success, result = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.error('Expected vote, received', extra={'extra': result})
            return None

        return result

    async def get_all_votes(self, bounty_guid, chain, api_key=None):
        """
        Get a vote from polyswamrd

        Args:
            bounty_guid (str): GUID of the bounty to retrieve the vote from
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        """
        path = '/bounties/{0}/votes'.format(bounty_guid)
        success, result = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.error('Expected vote, received', extra={'extra': result})
            return None

        return result

    async def post_vote(self, bounty_guid, votes, valid_bloom, chain, api_key=None):
        """Post a vote to polyswarmd.

        Args:
            bounty_guid (str): The bounty which we are voting on
            votes (List[bool]): Vote (malicious/benign) for each of the artifacts in the bounty
            valid_bloom (bool): Is the bloom filter reported by the bounty poster valid
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing emitted events
        """
        transaction = PostVoteTransaction(self.__client, bounty_guid, votes, valid_bloom)
        success, result = await transaction.send(chain, api_key=api_key)
        if not success or 'votes' not in result:
            logger.error('Expected vote, received', extra={'extra': result})

        return result.get('votes', [])

    async def settle_bounty(self, bounty_guid, chain, api_key=None):
        """Settle a bounty via polyswarmd

        Args:
            bounty_guid (str): The bounty which we are settling
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing emitted events
        """

        transaction = SettleBountyTransaction(self.__client, bounty_guid)
        success, result = await transaction.send(chain, api_key=api_key)
        if not success or 'transfers' not in result:
            logger.warning('No transfer event, received', extra={'extra': result})

        return result.get('transfers', [])
