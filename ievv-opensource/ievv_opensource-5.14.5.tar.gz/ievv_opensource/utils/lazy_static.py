

class LazyStatic(object):
    """
    Works just like the ``static`` template tag, but this is lazy
    (only evaluates in __str__), and can safely be used in settings.py etc.
    """
    def __init__(self, path):
        self.path = path

    def __str__(self):
        from django.templatetags.static import static
        return static(self.path)

    def __repr__(self):
        return 'LazyStatic({})'.format(self.path)
