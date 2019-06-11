#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper import ContractBase

AgreementTemplate = namedtuple(
    'AgreementTemplate',
    ('state', 'owner', 'updated_by', 'block_number_updated')
)


class TemplateStoreManager(ContractBase):
    """Class representing the TemplateStoreManager contract."""
    CONTRACT_NAME = 'TemplateStoreManager'

    def get_template(self, template_id):
        """
        Get the template for a given template id.

        :param template_id: id of the template, str
        :return:
        """
        template = self.contract_concise.getTemplate(template_id)
        if template and len(template) == 4:
            return AgreementTemplate(*template)

        return None

    def propose_template(self, template_id, from_account):
        """Propose a template.

        :param template_id: id of the template, str
        :param from_account: Account
        :return: bool
        """
        tx_hash = self.send_transaction(
            'proposeTemplate',
            (template_id,),
            transact={'from': from_account.address,
                      'passphrase': from_account.password})
        return self.get_tx_receipt(tx_hash).status == 1

    def approve_template(self, template_id, from_account):
        """
        Approve a template.

        :param template_id: id of the template, str
        :param from_account: Account
        :return:
        """
        tx_hash = self.send_transaction(
            'approveTemplate',
            (template_id,),
            transact={'from': from_account.address,
                      'passphrase': from_account.password})
        return self.get_tx_receipt(tx_hash).status == 1

    def revoke_template(self, template_id, from_account):
        """
        Revoke a template.

        :param template_id: id of the template, str
        :param from_account: Account
        :return: bool
        """
        tx_hash = self.send_transaction(
            'revokeTemplate',
            (template_id,),
            transact={'from': from_account.address,
                      'passphrase': from_account.password})
        return self.get_tx_receipt(tx_hash).status == 1

    def is_template_approved(self, template_id):
        """
        True if the template is approved.

        :param template_id: id of the template, str
        :return: bool
        """
        return self.contract_concise.isTemplateApproved(template_id)

    def get_num_templates(self):
        """
        Return the number of templates on-chain.

        :return: number of templates, int
        """
        return self.contract_concise.getTemplateListSize()
