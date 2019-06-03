""" Default URI Resolver
"""

from lxml import etree


class DefaultURIResolver(etree.Resolver):
    """ Default URI Resolver
    """
    def resolve(self, url, id, context):
        """ Resolve URL: returns to lxml default resolver.

        Args:
            url:
            id:
            context:

        Returns:

        """
        # return None to use the next registered resolver (or lxml default resolver)
        return None
