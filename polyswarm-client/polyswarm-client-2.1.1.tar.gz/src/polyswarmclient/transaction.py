import asyncio
import logging
from abc import ABCMeta, abstractmethod

from polyswarmclient.utils import exit

logger = logging.getLogger(__name__)

LOG_MSG_ENGINE_TOO_SLOW = ('PLEASE REVIEW YOUR SCANNING LOGIC. '
                           'Bounty inactive errors indicate that the microengine received the bounty, '
                           'but was unable to respond to the bounty within the time window. '
                           'Such errors are considered fatal during testing so you can easily identify them. '
                           'If your engine is unable to respond within the time window on the live PolySwarm '
                           'network, you risk losing the bid amount of the bounty at hand. We strongly '
                           'encourage you to review your artifact scan process to identify areas where engine '
                           'speed can be improved.')


class NonceManager:
    """Manages the nonce for some Ethereum chain"""

    def __init__(self, client, chain):
        self.base_nonce = 0
        self.client = client
        self.chain = chain

        self.needs_update = True
        self.nonce_lock = asyncio.Lock()
        self.in_progress = 0
        self.in_progress_condition = asyncio.Condition()

    async def acquire(self):
        """Acquires the nonce lock and updates base_nonce if needs_update is set"""
        await self.nonce_lock.acquire()

        if self.needs_update:
            async with self.in_progress_condition:
                # The wait inside here will release this lock, allowing finished() to work
                await self.in_progress_condition.wait_for(self.all_finished)

            # Wait for nonce to settle, can't rely on pending tx count
            last_nonce = -1
            while True:
                nonce = await self.client.get_base_nonce(self.chain)
                if nonce is not None and nonce == last_nonce:
                    break

                last_nonce = nonce
                await asyncio.sleep(1)

            if nonce is not None:
                self.base_nonce = nonce

            logger.debug('Updated nonce to %s on %s', nonce, self.chain)
            self.needs_update = False

    def all_finished(self):
        """Check that all tasks have finished"""
        return self.in_progress == 0

    async def finished(self):
        """Mark that some in-progress transaction finished on polyswarmd"""
        async with self.in_progress_condition:
            self.in_progress -= 1
            logger.debug('Tx resolved, in_progress: %s', self.in_progress)

            self.in_progress_condition.notify()

    async def reserve(self, amount=1):
        """Grab the next amount nonces.

        Args:
            amount (int): amount of sequential nonces to be claimed
        Returns
            (list[int]): a list of nonces to use
        """
        async with self:
            results = range(self.base_nonce, self.base_nonce + amount)
            self.base_nonce += amount

            # Inside nonce_lock so that there is no way the next acquire could miss an in progress
            async with self.in_progress_condition:
                # Note that a set of nonces is being used
                self.in_progress += 1
                logger.debug('New tx in flight, in_progress: %s', self.in_progress)

        return results

    def mark_update_nonce(self):
        """
        Call this when the nonce is out of sync.
        This sets the update flag to true.
        The next acquire after being set will trigger an update
        """
        self.needs_update = True

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc, tb):
        self.nonce_lock.release()


class AbstractTransaction(metaclass=ABCMeta):
    """Used to verify and post groups of transactions that make up a specific action.

    For instance, when approving some funds to move, and calling a contract function that will consumer them.
    """

    def __init__(self, client, verifiers):
        """Initialize a transaction

        Args:
            client (Client): Client object used to post transactions
            verifiers (list): Ordered verifiers for each transaction
        """
        self.client = client
        self.verifiers = verifiers

    async def send(self, chain, tries=2, api_key=None):
        """Make a transaction generating request to polyswarmd, then sign and post the transactions

        Args:
            chain (str): Which chain to operate on
            api_key (str): Override default API key
            tries (int): Number of times to retry before giving up
        Returns:
            (bool, obj): Tuple of boolean representing success, and response JSON parsed from polyswarmd
        """
        if api_key is None:
            api_key = self.client.api_key

        # Ensure we try at least once
        tries = max(tries, 1)

        # Step 1: Prepare the transaction, this is only done once
        success, results = await self.client.make_request('POST',
                                                          self.get_path(),
                                                          chain,
                                                          json=self.get_body(),
                                                          send_nonce=True,
                                                          api_key=api_key,
                                                          tries=tries)

        results = {} if results is None else results

        if not success or 'transactions' not in results:
            logger.error('Expected transactions, received', extra={'extra': results})
            return False, results

        transactions = results.get('transactions', [])
        if not self.verify(transactions):
            logger.critical("Transactions did not match expectations for the given request.",
                            extra={'extra': transactions})
            if self.client.tx_error_fatal:
                logger.critical(LOG_MSG_ENGINE_TOO_SLOW)
                exit(1)
            return False, {}

        # Keep around any extra data from the first request, such as nonce for assertion
        if 'transactions' in results:
            del results['transactions']

        orig_tries = tries
        post_errors = []
        get_errors = []
        while tries > 0:
            # Step 2: Update nonces, sign then post transactions
            txhashes, post_errors = await self.__sign_and_post_transactions(transactions, orig_tries, chain, api_key)
            if not txhashes:
                return False, {'errors': post_errors}

            # Step 3: At least one transaction was submitted successfully, get and verify the events it generated
            success, resync_nonces, results, get_errors = await self.__get_transactions(txhashes, orig_tries, chain,
                                                                                        api_key)
            if resync_nonces:
                continue

            return success, results

        return False, {'errors': post_errors + get_errors}

    async def __sign_and_post_transactions(self, transactions, tries, chain, api_key):
        """Signs and posts a set of transactions to Ethereum via polyswarmd

        Args:
            transactions (List[Transaction]): The transactions to sign and post
            tries (int): Number of times to retry before giving upyy
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing transaction status
        """
        nonce_manager = self.client.nonce_managers[chain]
        replace_nonce = True

        txhashes = []
        errors = []
        while tries > 0:
            tries -= 1

            # replace_nonce is True on first iteration and then after if nonce error occurs
            if replace_nonce:
                nonces = await nonce_manager.reserve(amount=len(transactions))
                for i, transaction in enumerate(transactions):
                    transaction['nonce'] = nonces[i]

            signed_txs = self.client.sign_transactions(transactions)
            raw_signed_txs = [bytes(tx['rawTransaction']).hex() for tx in signed_txs
                              if tx.get('rawTransaction', None) is not None]

            success, results = await self.client.make_request('POST', '/transactions', chain,
                                                              json={'transactions': raw_signed_txs}, api_key=api_key,
                                                              tries=1)

            if not success:
                # Known transaction errors seem to be a geth issue, don't spam log about it
                all_known_tx_errors = results is not None and \
                                      all(['known transaction' in r.get('message', '') for r in results if
                                           r.get('is_error')])

                if self.client.tx_error_fatal:
                    logger.critical('Received fatal transaction error during post.', extra={'extra': results})
                    logger.critical(LOG_MSG_ENGINE_TOO_SLOW)
                    exit(1)
                elif not all_known_tx_errors:
                    logger.error('Received transaction error during post', extra={'extra': results})

            results = [] if results is None else results

            if replace_nonce:
                await nonce_manager.finished()
                replace_nonce = False

            if len(results) != len(signed_txs):
                logger.warning('Transaction result length mismatch')

            txhashes = []
            errors = []
            for tx, result in zip(signed_txs, results):
                if tx.get('hash', None) is None:
                    logger.warning(f'Signed transaction missing txhash: {tx}')
                    continue

                txhash = bytes(tx['hash']).hex()
                message = result.get('message', '')
                is_error = result.get('is_error', False)

                # Known transaction errors seem to be a geth issue, don't retransmit in this case
                if is_error and 'known transaction' not in message.lower():
                    errors.append(message)
                else:
                    txhashes.append(txhash)

            if txhashes:
                if errors:
                    logger.warning('Transaction errors detected but some succeeded, fetching events',
                                   extra={'extra': errors})

                return txhashes, errors

            # Indicates nonce is too low, we can handle this now, resync nonces and retry
            if any(['invalid transaction error' in e.lower() for e in errors]):
                logger.error('Nonce desync detected during post, resyncing and trying again')
                nonce_manager.mark_update_nonce()
                replace_nonce = True

        return txhashes, errors

    async def __get_transactions(self, txhashes, tries, chain, api_key):
        """Get generated events or errors from receipts for a set of txhashes

        Args:
            txhashes (List[str]): The txhashes of the receipts to process
            tries (int): Number of times to retry before giving upyy
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            (bool, bool, dict, List[str]): Success, Resync nonce, Response JSON parsed from polyswarmd containing
                emitted events, errors
        """
        nonce_manager = self.client.nonce_managers[chain]

        success = False
        resync_nonce = False
        results = {}
        errors = []
        while tries > 0:
            tries -= 1

            success, results = await self.client.make_request('GET', '/transactions', chain,
                                                              json={'transactions': txhashes}, api_key=api_key, tries=1)
            if not success:
                if self.client.tx_error_fatal:
                    logger.critical('Received fatal transaction error during get.', extra={'extra': results})
                    logger.critical(LOG_MSG_ENGINE_TOO_SLOW)
                    exit(1)
                else:
                    logger.error('Received transaction error during get', extra={'extra': results})

            results = {} if results is None else results

            errors = results.get('errors', [])
            success = self.has_required_event(results)

            # Indicates nonce may be too high, if so resync nonces and try again at top level
            if any(['timeout during wait for receipt' in e.lower() for e in errors]):
                logger.error('Nonce desync detected during get, resyncing and trying again')
                nonce_manager.mark_update_nonce()
                resync_nonce = True
                break

            # Check to see if we failed to retrieve some receipts, retry the fetch if so
            if not success and any(['receipt' in e.lower() for e in errors]):
                logger.warning('Error fetching some receipts, retrying')
                continue

            if any(['transaction failed' in e.lower() for e in errors]):
                logger.error('Transaction failed due to bad parameters, not retrying', extra={'extra': errors})
                break

        return success, resync_nonce, results, errors

    @abstractmethod
    def has_required_event(self, transaction_events):
        """Checks for existence of events in transaction logs, ensuring successful completion

        Returns:
            True if the required event was in the list, false otherwise
        """
        raise NotImplementedError('has_required_event not implemented')

    @abstractmethod
    def get_path(self):
        """Get the path of the route to build this transaction

        Returns:
            str: Polyswarmd path to get the transaction data
        """
        raise NotImplementedError('get path is not implemented')

    @abstractmethod
    def get_body(self):
        """
        Build the payload to send to polyswarmd
        Returns:
            Dict payload
        """
        raise NotImplementedError('get body is not implemented')

    def verify(self, transactions):
        """Check the given transactions against known expectations

        Args:
            transactions (list) - A list of transactions from polyswarmd
        Returns:
            (bool): True if transactions match expectations. False otherwise
        """
        if len(transactions) != len(self.verifiers):
            return False

        return all([v.verify(tx) for v, tx in zip(self.verifiers, transactions)])
