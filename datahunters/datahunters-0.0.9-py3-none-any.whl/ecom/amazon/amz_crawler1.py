"""Crawler for amazon products.
"""

import amazonproduct

class AmazonCrawler(object):
    """
    """


amz_api = amazonproduct.API(
    access_key_id='AKIAIPBHBNDZV3LGYH5A',
    secret_access_key='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',
    associate_tag='eyes0ac-20',
    locale='us')

products = amz_api.item_search(
    search_index='Fashion', Keywords='dress', ResponseGroup='Large, Images')
print 'total products: {}'.format(len(products))
for product in products:
  print '{}'.format(product.ItemAttributes.Title)
