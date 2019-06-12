import plone.api as api


def run(_):
    catalog = api.portal.get_tool('portal_catalog')
    indexes = (
        'observation_sent_to_msc',
        'observation_sent_to_mse'
    )
    catalog.reindexIndex(indexes, REQUEST=None)
