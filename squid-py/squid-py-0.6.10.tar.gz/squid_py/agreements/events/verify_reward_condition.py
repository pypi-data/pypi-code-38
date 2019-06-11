def verify_reward_tokens(event, agreement_id, did, service_agreement, price, consumer_address,
                         publisher_account):
    """

    :param event: AttributeDict with the event data.
    :param agreement_id: id of the agreement, hex str
    :param did: DID, str
    :param service_agreement: ServiceAgreement instance
    :param price: Asset price, int
    :param consumer_address: ethereum account address of consumer, hex str
    :param publisher_account: Account instance of the publisher
    """
    # :TODO: verify that tokens were transfered to publisher
    pass



#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

verifyRewardTokens = verify_reward_tokens
