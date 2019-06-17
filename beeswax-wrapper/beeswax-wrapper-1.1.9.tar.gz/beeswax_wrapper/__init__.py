"""
API Classes for the Beeswax API
Usage:
>>> from beeswax_wrapper import BeeswaxAPI
>>> api = BeeswaxAPI()
>>> # get account information for an id
>>> api.accounts.retrieve(account_id=4)

>>> # get a list of campaigns
>>> api.campaigns.list()

>>> # delete a lineitem by id
>>> api.line_items.delete(line_item_id=62)

>>> # change user
>>> api.change_user('<username>', '<password>')
>>> # cookies are preserved per class
"""

from beeswax_wrapper.core.access import BeeswaxAPI, configure_endpoint

__all__ = ['BeeswaxAPI', 'configure_endpoint']
