class MemberAccessor(object):
    """Generic member accessor adapter implementation for Dexterity content
       objects.
    """
    def __init__(self, context):
        object.__setattr__(self, 'context', context)
        object.__setattr__(self, 'contact', context.contact.to_object)

    def __getattr__(self, name):
        if self.context.acquire_address and hasattr(self.contact, name):
            return getattr(self.contact, name, None)
        return getattr(self.context, name, None)
